package main

import (
	"debug/buildinfo"
	"encoding/json"
	"fmt"
	"os"
	"runtime/debug"
)

func fail(format string, arguments ...any) {
	fmt.Fprintf(os.Stderr, "read_go_binary_metadata: "+format+"\n", arguments...)
	os.Exit(1)
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: read_go_binary_metadata <go-binary>")
		os.Exit(2)
	}

	metadata, err := buildinfo.ReadFile(os.Args[1])
	if err != nil {
		fail("read Go build metadata: %v", err)
	}
	if metadata.Deps == nil {
		metadata.Deps = []*debug.Module{}
	}
	if metadata.Settings == nil {
		metadata.Settings = []debug.BuildSetting{}
	}

	encoder := json.NewEncoder(os.Stdout)
	encoder.SetEscapeHTML(false)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(metadata); err != nil {
		fail("encode Go build metadata: %v", err)
	}
}
