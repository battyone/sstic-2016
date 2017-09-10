CC ?= cc
DD ?= dd
PYTHON ?= python
RM ?= rm -f
SED ?= sed

all: level2/success.txt level3/success.txt level4/final_success.txt

# List Makefile targets with: sed -n 's/^\(\S.\+\):.*/\1/p' Makefile | tr ' ' $'\n' | tr % '*' | sed 's/\(.*\)/\t\t\1 \\/'
clean:
	$(RM) \
		level0/challenge.zip \
		level0/plugins/sham-data.js \
		level1/data.json \
		level1/SOS-Fant0me.zip \
		level1/radio.zip \
		level1/calc.zip \
		level1/SOS-Fant0me/SOS-Fant0me.pcap \
		level1/SOS-Fant0me/inflated-chunk-*.bin \
		level1/SOS-Fant0me/solution.zip \
		level1/SOS-Fant0me/solution.txt \
		level1/SOS-Fant0me/pass.code \
		level1/radio/rtl2832-f9.452000e+08-s1.000000e+06.bin.lzma \
		level1/radio/pass.code \
		level1/calc/SSTIC16.8xp \
		level1/calc/pass.code \
		level2/data.json \
		level2/foo.zip \
		level2/huge.zip \
		level2/loader.zip \
		level2/success.txt \
		level2/foo/foo.efi \
		level2/foo/pass.code \
		level2/huge/huge.tar \
		level2/huge/bruteforce_float.bin \
		level2/huge/pass.code \
		level2/loader/loader.exe \
		level2/loader/BizarroSSTIC.ttf \
		level2/loader/pass.code \
		level3/data.json \
		level3/ring.zip \
		level3/strange.zip \
		level3/usb.zip \
		level3/video.zip \
		level3/success.txt \
		level3/ring/ring.exe \
		level3/strange/a.out \
		level3/strange/196 \
		level3/strange/pass.code \
		level3/usb/img.bz2 \
		level3/usb/userSSTIC.bin \
		level3/usb/extracted_encrypted_data.bin \
		level3/usb/extracted_MBR.bin \
		level3/usb/extracted_part1.bin \
		level3/usb/extracted_part2.bin \
		level3/usb/extracted_part3.bin \
		level3/usb/extracted_part4.bin \
		level3/usb/drvSSTIC.sys \
		level3/usb/decrypted_chunk_*.bin \
		level3/usb/4.jpg \
		level3/usb/key \
		level3/usb/pass.code \
		level3/video/Stage_anti_APT_chez_Airlhes/Airlhes_screensaver_setup.exe \
		level3/video/Stage_anti_APT_chez_Airlhes/Airlhes_CYBER_SECRET_possible_exfiltration.mp4 \
		level3/video/Stage_anti_APT_chez_Airlhes/mission.txt \
		level4/data.json \
		level4/final.txt \
		level4/final_success.txt
	$(RM) -r level3/usb/__pycache__/

# Do the challenge
level0/challenge.pcap:
	mkdir -p $(@D)
	wget -O $@.tmp 'http://static.sstic.org/challenge2016/challenge.pcap'
	echo '0d39c9c1d09741a06ef8e35c0b63e538f60f8d5a7f995c7764e98a3ec595e46f $@.tmp' | sha256sum -c
	mv -f $@.tmp $@
	touch $@

# Extract the zip payload out of the pcap file
level0/challenge.zip: level0/challenge.pcap
	tshark -nr $< -w - tcp.srcport==80 | \
	tshark -nr - -q -z follow,tcp,hex,0 | \
	sed -n 's/^[0-9a-fA-F]*  \([0-9a-fA-F ]\{48\}\)  .*/\1/p' | \
	xxd -p -r | tail -c +96 > $@.tmp
	mv -f $@.tmp $@

level0/plugins/sham-data.js: level0/challenge.zip
	$(RM) $@
	cd $(<D) && unzip $(<F) plugins/sham-data.js
	touch $@

level1/data.json: level0/plugins/sham-data.js
	mkdir -p $(@D)
	sed -n 's/^this\.ssmdata={0:\(.*\)};/\1/p' $< > $@

level1/SOS-Fant0me.zip level1/radio.zip level1/calc.zip: level1/data.json extract_file_from_json.py
	$(PYTHON) extract_file_from_json.py $< $@

define inflate_zip_level
	mkdir -p $(<:%.zip=%)
	$(RM) $@
	cd $(<:%.zip=%) && unzip ../$(<F) $(@:$(<:%.zip=%)/%=%)
	touch $@
endef

level1/SOS-Fant0me/SOS-Fant0me.pcap: level1/SOS-Fant0me.zip
	$(inflate_zip_level)

# Extract random chunks with commands such as "make level1/SOS-Fant0me/inflated-chunk-0x2d68.bin"
level1/SOS-Fant0me/inflated-chunk-%.bin: level1/SOS-Fant0me/SOS-Fant0me.pcap
	$(PYTHON) -c 'import zlib;open("$@", "wb").write(zlib.decompress(open("$<", "rb").read()[$*:]))'

level1/SOS-Fant0me/solution.zip: level1/SOS-Fant0me/inflated-chunk-0x38947.bin
	tail -c +10 $< > $@

level1/SOS-Fant0me/solution.txt: level1/SOS-Fant0me/solution.zip
	$(RM) $@
	cd $(<D) && unzip -P 'Cyb3rSSTIC_2016' $(<F) $(@F)
	touch $@

level1/SOS-Fant0me/pass.code: level1/SOS-Fant0me/solution.txt
	cp -f $< $@

level1/radio/rtl2832-f9.452000e+08-s1.000000e+06.bin.lzma: level1/radio.zip
	$(inflate_zip_level)

level1/radio/pass.code: level1/radio/rtl2832-f9.452000e+08-s1.000000e+06.bin.lzma
	echo '1ac3d8c409e656380a06f6f2c6de6b4a' > $@

level1/calc/SSTIC16.8xp: level1/calc.zip
	$(inflate_zip_level)

level1/calc/pass.code: level1/calc/bruteforce_crc32.py level1/calc/SSTIC16.8xp
	cd $(<D) && $(PYTHON) $(<F)

level2/data.json: level1/data.json level1/SOS-Fant0me/pass.code level1/radio/pass.code level1/calc/pass.code
	mkdir -p $(@D)
	$(PYTHON) decrypt_next_level.py $@ $^

level2/foo.zip level2/huge.zip level2/loader.zip level2/success.txt: level2/data.json extract_file_from_json.py
	$(PYTHON) extract_file_from_json.py $< $@

level2/foo/foo.efi: level2/foo.zip
	$(inflate_zip_level)

level2/foo/pass.code: level2/foo/decrypt_secret.py level2/foo/foo.efi
	cd $(<D) && $(PYTHON) $(<F)

level2/huge/huge.tar: level2/huge.zip
	$(inflate_zip_level)

level2/huge/bruteforce_float.bin: level2/huge/bruteforce_float.c
	$(CC) $< -o $@

level2/huge/pass.code: level2/huge/huge.tar
	echo 'e574b514667f6ab2d83047bb871a54f5' > $@

level2/loader/loader.exe: level2/loader.zip
	$(inflate_zip_level)

level2/loader/BizarroSSTIC.ttf: level2/loader/loader.exe
	tail -c +67761 $< > $@

level2/loader/pass.code: level2/loader/parse_qmark_instr.py level2/loader/BizarroSSTIC.ttf
	cd $(<D) && $(PYTHON) $(<F)

level3/data.json: level2/data.json level2/foo/pass.code level2/huge/pass.code level2/loader/pass.code
	mkdir -p $(@D)
	$(PYTHON) decrypt_next_level.py $@ $^

level3/ring.zip level3/strange.zip level3/usb.zip level3/video.zip level3/success.txt: level3/data.json extract_file_from_json.py
	$(PYTHON) extract_file_from_json.py $< $@

level3/ring/ring.exe: level3/ring.zip
	$(inflate_zip_level)

level3/strange/a.out level3/strange/196: level3/strange.zip
	$(inflate_zip_level)

level3/strange/pass.code: level3/strange/bruteforce_digits.py level3/strange/a.out level3/strange/196
	cd $(<D) && $(PYTHON) $(<F)

level3/usb/img.bz2 level3/usb/userSSTIC.bin: level3/usb.zip
	$(inflate_zip_level)

level3/usb/extracted_encrypted_data.bin level3/usb/extracted_MBR.bin level3/usb/extracted_part1.bin level3/usb/extracted_part2.bin level3/usb/extracted_part3.bin level3/usb/extracted_part4.bin: level3/usb/extract_parts_and_holes.py level3/usb/img.bz2
	cd $(<D) && $(PYTHON) $(<F)

level3/usb/drvSSTIC.sys: level3/usb/userSSTIC.bin
	$(DD) if=$< of=$@ bs=1 skip=113328 count=19280

level3/usb/decrypted_chunk_%.bin: level3/usb/decrypt.py level3/usb/extracted_encrypted_data.bin level3/usb/drvSSTIC.sys
	cd $(<D) && $(PYTHON) $(<F)

level3/usb/4.jpg level3/usb/key: level3/usb/decrypted_chunk_4.bin
	$(RM) $@
	cd $(<D) && unzip -P '!WooYouAreSuchAnAwesomeGuy!' $(<F) $(@F)
	touch $@

level3/usb/pass.code: level3/usb/key
	xxd -p $< > $@

level3/video/Stage_anti_APT_chez_Airlhes/Airlhes_screensaver_setup.exe level3/video/Stage_anti_APT_chez_Airlhes/Airlhes_CYBER_SECRET_possible_exfiltration.mp4 level3/video/Stage_anti_APT_chez_Airlhes/mission.txt: level3/video.zip
	$(inflate_zip_level)

level4/data.json: level3/data.json level3/strange/pass.code level3/usb/pass.code
	mkdir -p $(@D)
	$(PYTHON) decrypt_next_level.py $@ $^

level4/final.txt: level4/data.json extract_file_from_json.py
	$(PYTHON) extract_file_from_json.py $< $@

level4/final_success.txt: level4/final.txt
	(head -n -1 $< && (tail -n 1 $< | tr a-zA-Z n-za-mN-ZA-M)) > $@

.PHONY: clean all
