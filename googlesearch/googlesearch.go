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

// buildClient initializes the HTTP client
func (c *SearchClient) buildClient() error {
    if c.httpClient != nil {
        return nil
    }

    c.httpClient = &http.Client{
        Transport: &http.Transport{},
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

	fmt.Println("searchURL:", searchURL)
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
	req.Header.Set("Cookie", "AEC=AVcja2e0osgVZ2MvTTHJYpLp4yhID9N0TRFsReOdxd5tCSFUs7NPTSRuZQ; NID=521=NQPOecq6prPLWgFgmx7jyla-RUBYpeKwu6oNkRIf6m9rusePsivbTTJ_f9l4cNw2SlRKcJBQBr_LayeW8ruNTP18Qb7KgkTa5yMmcns5yFZwybs1FdxMmLZ9Am9Ae9bs9yKWsuQBQV84bO_fokHv0Sqn6IbXAsng725pMDWGFbJC7Sb02xzd8Ahl0RE4lLGavVeV1G85n7zGbnFNKqkeVkbVZXm8zkwoNv-mKcqea3_oo9eIikQb7w1ZeeECNMv-e-duQio")

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
    // Regular expression pattern for valid URLs, excluding JavaScript and unwanted patterns
    urlPattern := regexp.MustCompile(`https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)`)
    
    // Find all matches in the content
    matches := urlPattern.FindAllString(content, -1)
    
    // Create a map to store unique URLs
    uniqueURLs := make(map[string]bool)
    
    // Create a slice to store the final result
    var results []string
    
    // Process each match
    for _, match := range matches {
        // Clean up the URL
        url := strings.TrimRight(match, ".,!?:;'\"&amp")
        
        // Skip if URL contains unwanted patterns
        if strings.Contains(url, "google.com") ||
           strings.Contains(url, "gstatic.com") ||
           strings.Contains(url, "accounts.google") ||
           strings.Contains(url, "support.google") ||
           strings.Contains(url, "policies.google") {
            continue
        }
        
        // Add URL to results if we haven't seen it before
        if !uniqueURLs[url] {
            uniqueURLs[url] = true
            results = append(results, url)
        }
    }
    
    return results
}

func getRandomUserAgent() string {
	rand.Seed(time.Now().UnixNano())
	return userAgents[rand.Intn(len(userAgents))]
}