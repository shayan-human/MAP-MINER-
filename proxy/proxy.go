package proxy

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

type Manager struct {
	proxies     []string
	working     []string
	failed      map[string]bool
	mu          sync.RWMutex
	strictMode  bool
	healthCheck bool
}

type Option func(*Manager)

func WithStrictMode(enabled bool) Option {
	return func(pm *Manager) {
		pm.strictMode = enabled
	}
}

func WithHealthCheck(enabled bool) Option {
	return func(pm *Manager) {
		pm.healthCheck = enabled
	}
}

func NewManager(proxies []string, opts ...Option) *Manager {
	pm := &Manager{
		proxies:     make([]string, 0, len(proxies)),
		working:     make([]string, 0, len(proxies)),
		failed:      make(map[string]bool),
		strictMode:  false,
		healthCheck: true,
	}

	for _, opt := range opts {
		opt(pm)
	}

	for _, p := range proxies {
		p = strings.TrimSpace(p)
		if p != "" {
			pm.proxies = append(pm.proxies, p)
		}
	}

	return pm
}

func (pm *Manager) GetProxies() []string {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	return pm.working
}

func (pm *Manager) GetAllProxies() []string {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	return pm.proxies
}

func (pm *Manager) IsStrictMode() bool {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	return pm.strictMode
}

func (pm *Manager) MarkFailed(proxy string) {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	pm.failed[proxy] = true

	for i, p := range pm.working {
		if p == proxy {
			pm.working = append(pm.working[:i], pm.working[i+1:]...)
			break
		}
	}
}

func (pm *Manager) MarkWorking(proxy string) {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	for _, p := range pm.working {
		if p == proxy {
			return
		}
	}

	pm.working = append(pm.working, proxy)
}

func (pm *Manager) HasWorkingProxies() bool {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	return len(pm.working) > 0
}

func (pm *Manager) CountWorking() int {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	return len(pm.working)
}

func (pm *Manager) CountFailed() int {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	return len(pm.failed)
}

func (pm *Manager) Total() int {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	return len(pm.proxies)
}

func (pm *Manager) ValidateAndFilter(_ context.Context) error {
	if len(pm.proxies) == 0 {
		return nil
	}

	if !pm.healthCheck {
		pm.working = pm.proxies
		log.Printf("[Manager] Health check disabled, using all %d proxies", len(pm.proxies))

		return nil
	}

	log.Printf("[Manager] Starting health check for %d proxies...", len(pm.proxies))

	var wg sync.WaitGroup

	var mu sync.Mutex

	validProxies := make([]string, 0)

	testURL := "https://www.google.com"
	timeout := 10 * time.Second

	for _, proxy := range pm.proxies {
		wg.Add(1)

		go func(p string) {
			defer wg.Done()

			isValid := pm.checkProxy(p, testURL, timeout)

			mu.Lock()

			if isValid {
				validProxies = append(validProxies, p)
			}
		}(proxy)
	}

	wg.Wait()

	pm.mu.Lock()
	pm.working = validProxies
	pm.mu.Unlock()

	if len(pm.working) == 0 {
		if pm.strictMode {
			return fmt.Errorf("%w: all %d proxies failed health check", ErrAllProxiesFailed, len(pm.proxies))
		}

		log.Printf("[Manager] WARNING: All proxies failed health check, no proxies available")

		return nil
	}

	log.Printf("[Manager] Health check complete: %d/%d proxies working", len(pm.working), len(pm.proxies))

	if len(pm.working) < len(pm.proxies) {
		failed := len(pm.proxies) - len(pm.working)
		log.Printf("[Manager] %d proxy(s) failed and will be skipped", failed)
	}

	return nil
}

func (pm *Manager) checkProxy(proxy, testURL string, timeout time.Duration) bool {
	client := &http.Client{
		Timeout: timeout,
		Transport: &http.Transport{
			Proxy: func(*http.Request) (*url.URL, error) {
				return url.Parse(proxy)
			},
		},
	}

	req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, testURL, http.NoBody)
	if err != nil {
		return false
	}

	resp, err := client.Do(req)
	if err != nil {
		return false
	}

	defer func() {
		_, _ = io.Copy(io.Discard, resp.Body)
		resp.Body.Close()
	}()

	return resp.StatusCode < 500
}

func (pm *Manager) GetNextProxy() (string, error) {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	if len(pm.working) == 0 {
		if pm.strictMode {
			return "", fmt.Errorf("%w: no working proxies available", ErrNoWorkingProxies)
		}

		return "", ErrNoWorkingProxies
	}

	proxy := pm.working[0]
	pm.working = append(pm.working[1:], proxy)

	return proxy, nil
}

func (pm *Manager) RoundRobinGet() ([]string, error) {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	if len(pm.working) == 0 {
		if pm.strictMode {
			return nil, fmt.Errorf("%w: no working proxies available", ErrNoWorkingProxies)
		}

		return nil, ErrNoWorkingProxies
	}

	return pm.working, nil
}

func (pm *Manager) ValidateProxyFormat(proxy string) error {
	if proxy == "" {
		return ErrEmptyProxy
	}

	parsed, err := url.Parse(proxy)
	if err != nil {
		return fmt.Errorf("%w: %v", ErrInvalidProxyFormat, err)
	}

	scheme := parsed.Scheme
	if scheme != "http" && scheme != "https" && scheme != "socks5" && scheme != "socks5h" {
		return fmt.Errorf("%w: unsupported scheme '%s' (supported: http, https, socks5, socks5h)", ErrInvalidProxyFormat, scheme)
	}

	if parsed.Host == "" {
		return fmt.Errorf("%w: missing host:port", ErrInvalidProxyFormat)
	}

	return nil
}

func (pm *Manager) ValidateAllProxies() []error {
	var errors []error

	for _, proxy := range pm.proxies {
		if err := pm.ValidateProxyFormat(proxy); err != nil {
			errors = append(errors, fmt.Errorf("proxy '%s': %w", proxy, err))
		}
	}

	return errors
}

type Error string

func (e Error) Error() string {
	return string(e)
}

const (
	ErrNoWorkingProxies   Error = "no working proxies available"
	ErrAllProxiesFailed   Error = "all proxies failed"
	ErrEmptyProxy         Error = "empty proxy string"
	ErrInvalidProxyFormat Error = "invalid proxy format"
)

func ParseProxiesFromInput(input string) []string {
	var proxies []string

	lines := strings.Split(input, "\n")
	for _, line := range lines {
		proxy := strings.TrimSpace(line)
		if proxy != "" {
			proxy = normalizeProxy(proxy)
			proxies = append(proxies, proxy)
		}
	}

	return proxies
}

func normalizeProxy(proxy string) string {
	proxy = strings.TrimSpace(proxy)

	if strings.Contains(proxy, "://") {
		return proxy
	}

	if strings.Contains(proxy, "@") {
		parts := strings.Split(proxy, "@")
		if len(parts) == 2 {
			return "http://" + proxy
		}
	}

	return "http://" + proxy
}
