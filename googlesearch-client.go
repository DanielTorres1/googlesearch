package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"
	"github.com/fatih/color"
	"googlesearch/googlesearch"
)

const banner = `
Google search                                                    

Autor: Daniel Torres Sandi
`
//const googleURL = "https://ipt5gxa9dh.execute-api.us-east-1.amazonaws.com/googleProxy"
const googleURL = "https://google.com"

var (
	term     = flag.String("t", "", "Search term")
	outFile  = flag.String("o", "", "Output file")
	logFile  = flag.String("l", "", "Log file")
	date     = flag.String("d", "", "Date filter")
	help     = flag.Bool("h", false, "Show help")
	debug    = false
)

func usage() {
	fmt.Println(banner)
	fmt.Println("Usage:")
	fmt.Println("-t : Search term")
	fmt.Println("-o : Output file")
	fmt.Println("-h : Help")
	fmt.Println("-d : Date")
	fmt.Println("-l : Log file")
	fmt.Println("Example: googlesearch-client -t 'site:gob.bo' -l google2.html -o lista.txt")
}

func main() {
	flag.Parse()

	if *help || flag.NFlag() == 0 {
		usage()
		return
	}

	yellow := color.New(color.FgYellow).SprintfFunc()
	blue := color.New(color.FgBlue).SprintfFunc()

	fmt.Println(yellow("\t[+] Search term: %s", *term))
	fmt.Println(blue("\t[+] Searching on Google"))

	client := googlesearch.NewSearchClient()
	client.GoogleURL = googleURL

	page := 0
	for {
		printpage := page + 1
		fmt.Printf("\t\t[+] page: %d\n", printpage)

		// Perform search
		opts := googlesearch.SearchOptions{
			Keyword:  *term,
			Start:    strconv.Itoa(page * 100),
			LogFile:  *logFile,
			Date:     *date,
		}

		list, err := client.Search(opts)
		if err != nil {
			fmt.Printf("Error performing search: %v\n", err)
			os.Exit(1)
		}

		// Process and save results
		urls := strings.Split(list, ";")
		if err := appendToFile(*outFile, urls); err != nil {
			fmt.Printf("Error writing to output file: %v\n", err)
			os.Exit(1)
		}

		for _, url := range urls {
			fmt.Println(url)
		}

		// Check for next page
		hasNextPage, err := checkNextPage(*logFile)
		if err != nil {
			fmt.Printf("Error checking next page: %v\n", err)
			os.Exit(1)
		}

		if !hasNextPage {
			break
		}

		page++
		time.Sleep(1 * time.Second)
	}
}

func appendToFile(filename string, urls []string) error {
	file, err := os.OpenFile(filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	for _, url := range urls {
		url = strings.TrimSpace(url)
		if url != "" {
			if _, err := writer.WriteString(url + "\n"); err != nil {
				return err
			}
		}
	}
	return writer.Flush()
}

func checkNextPage(logFile string) (bool, error) {
	content, err := os.ReadFile(logFile)
	if err != nil {
		return false, err
	}

	// Check for next page indicators
	pattern := regexp.MustCompile(`(?i)Next &gt;|More results|>&gt;</`)
	matches := pattern.FindAll(content, -1)

	if debug {
		fmt.Printf("next_link count: %d\n", len(matches))
	}

	return len(matches) > 0, nil
}