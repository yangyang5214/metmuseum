package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/hashicorp/go-retryablehttp"
	"github.com/tidwall/gjson"
	"io"
	"io/ioutil"
	"log"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"
)

const targetDir = "/home/pi/sda1/metmuseum"
const keywordDir string = "keywords"
const keywordIdsDir string = "keyword_ids"

var wg sync.WaitGroup

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

func isFileExists(path string) bool {
	_, err := os.Stat(path)
	if err != nil {
		if os.IsExist(err) {
			return true
		}
		return false
	}
	return true
}

func saveObject(data string) {
	images := gjson.Get(data, "additionalImages").Array()
	primaryImage := gjson.Get(data, "primaryImage")
	images = append(images, primaryImage)

	objectID := gjson.Get(data, "objectID").String()
	localTargetDir := filepath.Join(targetDir, "objects", objectID)

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

	if len(images) > 0 {
		wg.Add(len(images))

		for _, imageUrl := range images {
			go downloadImage(imageUrl.String(), localTargetDir)
		}
	}
	saveFile(filepath.Join(localTargetDir, "flag"), bytes.NewReader([]byte("")))
}

func processObjectById(objectId string) {
	defer wg.Done()
	//use local cache
	localTargetDir := filepath.Join(targetDir, "objects", objectId, "flag")
	if isFileExists(localTargetDir) {
		log.Printf("Skip objectId: 【%s】", objectId)
		return
	}
	respJson := getObjectById(objectId)
	saveObject(respJson)
}

//Load all keywords, then get all object_ids
func fetchAllIds() {
	log.Println("start running  🚗 🚗 🚗 🚗 🚗 🚗")
	allKeywords := loadAllKeywords()
	log.Printf("Loading allKeywords length: %d", len(allKeywords))
	wg.Add(len(allKeywords))
	for key := range allKeywords {
		keyFileName := filepath.Join(keywordIdsDir, key)
		if isFileExists(keyFileName) {
			wg.Done()
			log.Printf("key 【%s】 cached, skip", key)
			continue
		}
		idsObj := getIdsByKeyword(key)
		objectIDs := gjson.Get(idsObj, "objectIDs").Array()
		var ids []string
		for _, item := range objectIDs {
			ids = append(ids, item.String())
		}
		jsonStr, _ := json.Marshal(ids)
		saveFile(keyFileName, bytes.NewReader(jsonStr))
		wg.Done()
	}
	wg.Wait()
}

//加载所有的 object_ids, 获取数据
func fetchAllObject() {
	var dirNames, _ = ioutil.ReadDir(keywordIdsDir)
	keywordIdsMap := map[string]bool{}
	for _, f := range dirNames {
		data, _ := ioutil.ReadFile(path.Join(keywordIdsDir, f.Name()))
		var arr []string
		err := json.Unmarshal(data, &arr)
		if err != nil {
			//ignore
		}
		for _, keyword := range arr {
			keywordIdsMap[keyword] = true
		}
	}
	log.Printf("Loading all_object_ids length: %d", len(keywordIdsMap))

	flag := 0
	for objectId := range keywordIdsMap {
		flag++
		wg.Add(1)
		go processObjectById(objectId)

		//控制并发？不知道对不对。。。
		if flag%100 == 0 {
			log.Printf("wait ...")
			wg.Wait()
		}
	}
	wg.Wait()
}

func main() {
	//fetchAllIds()
	fetchAllObject()
}
