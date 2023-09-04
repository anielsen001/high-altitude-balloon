# list the subdirectories to entire and run make
SUBDIRS = \
	_sources

.PHONY: all $(SUBDIRS)

all: $(SUBDIRS)

$(SUBDIRS): 
	$(MAKE) -C $@

