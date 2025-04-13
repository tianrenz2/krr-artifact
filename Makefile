
CURRENT_DIR := $(shell pwd)
schemes := baseline,kernel_rr,whole_system_rr

$(info CURRENT_DIR = $(CURRENT_DIR))

.PHONY: all
all: build

# Build target - executes the setup script
.PHONY: build
build:
	bash scripts/setup.sh

test_rocksdb:
	bash scripts/rocksdb_benchmark.sh $(CURRENT_DIR) rocksdb $(schemes)

test_rocksdb_spdk:
	bash scripts/rocksdb_benchmark.sh $(CURRENT_DIR)  rocksdb-spdk $(schemes)

# Clean target (optional)
.PHONY: clean
clean:
	# Add commands to clean build artifacts
	@echo "Cleaning up..."
