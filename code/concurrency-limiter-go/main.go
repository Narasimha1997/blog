package main

import (
	"fmt"
	"math/rand"
	"runtime"
	"time"
)

const NGoroutines = 6

func notifyComplete(notifier chan bool) {
	// notify the completion by consuming a boolean from the buffered channel
	<-notifier
}

func processor(sleepTime time.Duration, notifier chan bool) {
	// make sure this always runs
	notifyComplete(notifier)
	// sleep for the given duration (just for the sake of providing an example)
	time.Sleep(sleepTime)
}

func main() {
	// create the notifier channel
	notifier := make(chan bool, NGoroutines)

	logger := func() {
		for {
			time.Sleep(5 * time.Second)
			fmt.Printf("number_of_goroutines=%d", runtime.NumGoroutine())
		}
	}

	// log number of go-routines every 5 seconds
	go logger()

	for {
		// random sleep time between 1-5 seconds
		sleepTime := (rand.Int() % 5) + 1
		// pass a boolean into the notifier for the go-routine to consume once it has
		// finished execution
		notifier <- true
		go processor(time.Duration(sleepTime)*time.Second, notifier)
	}
}
