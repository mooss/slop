package main

import (
	"flag"
	"fmt"
	"os"
	"runtime/pprof"
)

func main() {
	///////////////
	// Profiling //
	cpuProfile := flag.String("cpuprofile", "", "write cpu profile to file")
	memProfile := flag.String("memprofile", "", "write memory profile to file")
	flag.Parse()

	if *cpuProfile != "" {
		f, err := os.Create(*cpuProfile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Could not create CPU profile: %v\n", err)
			os.Exit(1)
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}

	if *memProfile != "" {
		defer func() {
			f, err := os.Create(*memProfile)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Could not create memory profile: %v\n", err)
				return
			}
			defer f.Close()
			pprof.WriteHeapProfile(f)
		}()
	}

	/////////////////////
	// Args validation //

	args := flag.Args()
	binary := os.Args[0]

	if len(args) != 1 {
		fmt.Fprintf(os.Stderr, "Usage: %s <filename>\n", binary)
		os.Exit(1)
	}

	///////////////
	// Execution //

	filename := args[0]
	fmt.Println(filename)
}
