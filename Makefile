.PHONY: help tree status

help:
	@echo "Available commands:"
	@echo "  make tree    Show project folder structure"
	@echo "  make status  Show git status"

tree:
	tree -L 3

status:
	git status
