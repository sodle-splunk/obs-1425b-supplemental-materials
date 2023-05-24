.PHONY: playbook

clean:
	rm -f build/*.tgz

playbook:
	# We disable the "copyfile" functionality of tar
	# on MacOS hosts, because it creates hidden files
	# that SOAR can't handle.
	export COPYFILE_DISABLE=1 && \
	cd playbook && \
	pwd && \
	tar czf ../build/obs1425b.tgz \
		"OBS1425B - Sample Playbook.json" \
		"OBS1425B - Sample Playbook.py"