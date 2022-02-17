package main

import (
	"bufio"
	"bytes"
	"fmt"
	"github.com/hashicorp/go-retryablehttp"
	"github.com/tidwall/gjson"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"
)

const targetDir = "/tmp/metmuseum"
const keywordDir string = "keywords"

var wg sync.WaitGroup

var httpClient = http.Client{
	Timeout: 1 * time.Minute,
	Transport: &http.Transport{
		TLSHandshakeTimeout: 1 * time.Minute,
		DisableKeepAlives:   true,
	},
}

func getIdsByKeyword(keyword string) string {
	url := fmt.Sprintf("https://collectionapi.metmuseum.org/public/collection/v1/search?q=%s", keyword)
	return httpGet(url)
}

func httpGet(url string) string {
	resp, err := retryablehttp.Get(url)
	if err != nil {
		panic(err)
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	return string(body)
}

func getObjectById(objectId string) string {
	url := fmt.Sprintf("https://collectionapi.metmuseum.org/public/collection/v1/objects/%s", objectId)
	return httpGet(url)
}

func loadAllKeywords() map[string]bool {
	var dirNames, _ = ioutil.ReadDir(keywordDir)
	keywordMap := map[string]bool{}
	for _, name := range dirNames {
		log.Printf("Loading %s file keywords", name.Name())
		data, _ := ioutil.ReadFile(path.Join(keywordDir, name.Name()))
		content := string(data)
		for _, keyword := range strings.Split(content, "\n") {
			keywordMap[keyword] = true
		}
	}
	return keywordMap
}

func downloadImage(url string, fileDir string) {
	defer wg.Done()
	if url == "" {
		return
	}
	log.Printf("Donwload image: %s", url)
	nowTs := strconv.FormatInt(time.Now().UnixNano(), 10)
	fileName := filepath.Join(fileDir, fmt.Sprintf("%s.jpg", nowTs))
	saveFile(fileName, bytes.NewReader([]byte(httpGet(url))))
}

func saveFile(fileName string, bytes io.Reader) {
	out, _ := os.Create(fileName)
	wt := bufio.NewWriter(out)
	defer out.Close()
	_, err := io.Copy(wt, bytes)
	if err != nil {
		log.Panic(err)
	}
	err = wt.Flush()
	if err != nil {
		log.Panic(err)
	}
}

func saveObject(keyword string, data string) {
	images := gjson.Get(data, "additionalImages").Array()
	primaryImage := gjson.Get(data, "primaryImage")
	images = append(images, primaryImage)

	objectID := gjson.Get(data, "objectID").String()
	localTargetDir := filepath.Join(targetDir, keyword, objectID)

	targetFileName := filepath.Join(localTargetDir, fmt.Sprintf("%s.json", objectID))

	if _, err := os.Stat(localTargetDir); os.IsNotExist(err) {
		err := os.MkdirAll(localTargetDir, os.ModePerm)
		if err != nil {
			log.Panic(err)
		}
	}

	err := ioutil.WriteFile(targetFileName, []byte(data), os.ModePerm)
	if err != nil {
		log.Panic(err)
	}

	if len(images) < 1 {
		return
	}

	wg.Add(len(images))

	for _, imageUrl := range images {
		go downloadImage(imageUrl.String(), localTargetDir)
	}
}

func processObjectById(objectId string, key string) {
	defer wg.Done()
	respJson := getObjectById(objectId)
	saveObject(key, respJson)
}

func main() {
	log.Println("start running  🚗 🚗 🚗 🚗 🚗 🚗")
	allKeywords := loadAllKeywords()
	log.Printf("Loading allKeywords length: %d", len(allKeywords))
	for key := range allKeywords {
		idsObj := getIdsByKeyword(key)
		objectIDs := gjson.Get(idsObj, "objectIDs").Array()

		//todo
		objectIDs = objectIDs[:10]

		log.Printf("Loading %s,  objectIDs length: %d", key, len(objectIDs))
		wg.Add(len(objectIDs))
		for _, item := range objectIDs {
			objectId := item.String()
			go processObjectById(objectId, key)
		}
	}
	wg.Wait()
}
