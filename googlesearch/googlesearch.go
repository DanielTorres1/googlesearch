package googlesearch

import (
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"

	"golang.org/x/net/proxy"
)

// SearchClient represents the Google search client configuration
type SearchClient struct {
	ProxyHost  string
	ProxyPort  string
	ProxyUser  string
	ProxyPass  string
	GoogleURL  string
	UserAgent  string
	httpClient *http.Client
}

// SearchOptions contains the parameters for performing a search
type SearchOptions struct {
	Keyword  string
	Date     string
	Lang     string
	Filter   string
	Start    string
	LogFile  string
}

var userAgents = []string{
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36",
}

// NewSearchClient creates a new instance of SearchClient with default values
func NewSearchClient() *SearchClient {
	return &SearchClient{
		GoogleURL: "https://h04ix0nbs5.execute-api.us-east-1.amazonaws.com/googleProxy",
		UserAgent: getRandomUserAgent(),
	}
}

// SetProxy configures the proxy settings for the client
func (c *SearchClient) SetProxy(host, port, user, pass string) {
	c.ProxyHost = host
	c.ProxyPort = port
	c.ProxyUser = user
	c.ProxyPass = pass
}

// buildClient initializes the HTTP client with proxy settings if configured
func (c *SearchClient) buildClient() error {
	if c.httpClient != nil {
		return nil
	}

	transport := &http.Transport{}

	if c.ProxyHost != "" {
		if c.ProxyHost == "tor" {
			// Configure for Tor
			dialer, err := proxy.SOCKS5("tcp", "localhost:9050", nil, proxy.Direct)
			if err != nil {
				return fmt.Errorf("error creating tor proxy dialer: %v", err)
			}
			transport.Dial = dialer.Dial
		} else {
			// Configure standard proxy
			proxyURL := &url.URL{}
			if c.ProxyUser != "" && c.ProxyPass != "" {
				proxyURL = &url.URL{
					Scheme: "http",
					User:   url.UserPassword(c.ProxyUser, c.ProxyPass),
					Host:   fmt.Sprintf("%s:%s", c.ProxyHost, c.ProxyPort),
				}
			} else {
				proxyURL = &url.URL{
					Scheme: "http",
					Host:   fmt.Sprintf("%s:%s", c.ProxyHost, c.ProxyPort),
				}
			}
			transport.Proxy = http.ProxyURL(proxyURL)
		}
	}

	c.httpClient = &http.Client{
		Transport: transport,
		Timeout:   10 * time.Second,
	}

	return nil
}

// Search performs a Google search with the specified options
func (c *SearchClient) Search(opts SearchOptions) (string, error) {
	if err := c.buildClient(); err != nil {
		return "", err
	}

	searchURL := fmt.Sprintf("%s/search?q=%s&oq=%s&num=100&filter=0&sourceid=chrome&ie=UTF-8",
		c.GoogleURL, url.QueryEscape(opts.Keyword), url.QueryEscape(opts.Keyword))

	if opts.Start != "" {
		searchURL += "&start=" + opts.Start
	}
	if opts.Date != "" {
		searchURL += "&tbs=qdr:" + opts.Date
	}
	if opts.Lang != "" {
		searchURL += "&hl=" + opts.Lang
	}

	maxRetries := 7
	for tries := 0; tries < maxRetries; tries++ {
		content, err := c.makeRequest(searchURL)
		if err != nil {
			if tries == maxRetries-1 {
				return "", err
			}
			time.Sleep(5 * time.Second)
			continue
		}

		if strings.Contains(content, "Our systems have detected unusual traffic from your computer network") {
			fmt.Println("Captcha detected!")
			time.Sleep(60 * time.Second)
			continue
		}

		// Save content to file for processing
		if err := ioutil.WriteFile("google.html", []byte(content), 0644); err != nil {
			return "", err
		}

		urls := extractURLs(content)
		if opts.LogFile != "" {
			if err := os.Rename("google.html", opts.LogFile); err != nil {
				fmt.Printf("Warning: Could not rename log file: %v\n", err)
			}
		}

		return strings.Join(urls, ";"), nil
	}

	return "", fmt.Errorf("max retries exceeded")
}

func (c *SearchClient) makeRequest(url string) (string, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", err
	}

	req.Header.Set("User-Agent", c.UserAgent)
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("Accept-Language", "en-US,en;q=0.5")
	req.Header.Set("Connection", "keep-alive")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

func extractURLs(content string) []string {
	re := regexp.MustCompile(`href="(https?://[^"&]*)"`)
	matches := re.FindAllStringSubmatch(content, -1)

	var urls []string
	seen := make(map[string]bool)

	for _, match := range matches {
		if len(match) < 2 {
			continue
		}
		
		urlStr := match[1]
		if strings.Contains(urlStr, "google.") || strings.Contains(urlStr, "search?") {
			continue
		}

		if !seen[urlStr] {
			seen[urlStr] = true
			decodedURL, err := url.QueryUnescape(urlStr)
			if err == nil {
				urls = append(urls, decodedURL)
			}
		}
	}

	return urls
}

func getRandomUserAgent() string {
	rand.Seed(time.Now().UnixNano())
	return userAgents[rand.Intn(len(userAgents))]
}