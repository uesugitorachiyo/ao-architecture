package main

import (
	"debug/buildinfo"
	"encoding/json"
	"fmt"
	"os"
	"runtime/debug"
)

type canonicalModule struct {
	Path    string           `json:"Path"`
	Version string           `json:"Version"`
	Sum     string           `json:"Sum"`
	Replace *canonicalModule `json:"Replace,omitempty"`
}

type canonicalSetting struct {
	Key   string `json:"Key"`
	Value string `json:"Value"`
}

type canonicalBuildInfo struct {
	GoVersion string             `json:"GoVersion"`
	Path      string             `json:"Path"`
	Main      canonicalModule    `json:"Main"`
	Deps      []canonicalModule  `json:"Deps"`
	Settings  []canonicalSetting `json:"Settings"`
}

func canonicalizeModule(module *debug.Module) *canonicalModule {
	if module == nil {
		return nil
	}
	return &canonicalModule{
		Path:    module.Path,
		Version: module.Version,
		Sum:     module.Sum,
		Replace: canonicalizeModule(module.Replace),
	}
}

func canonicalizeBuildInfo(metadata *debug.BuildInfo) canonicalBuildInfo {
	dependencies := make([]canonicalModule, 0, len(metadata.Deps))
	for _, dependency := range metadata.Deps {
		canonical := canonicalizeModule(dependency)
		if canonical != nil {
			dependencies = append(dependencies, *canonical)
		}
	}
	settings := make([]canonicalSetting, 0, len(metadata.Settings))
	for _, setting := range metadata.Settings {
		settings = append(settings, canonicalSetting{Key: setting.Key, Value: setting.Value})
	}
	main := canonicalizeModule(&metadata.Main)
	return canonicalBuildInfo{
		GoVersion: metadata.GoVersion,
		Path:      metadata.Path,
		Main:      *main,
		Deps:      dependencies,
		Settings:  settings,
	}
}

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
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetEscapeHTML(false)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(canonicalizeBuildInfo(metadata)); err != nil {
		fail("encode Go build metadata: %v", err)
	}
}
