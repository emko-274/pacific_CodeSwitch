# eng_mri

This package identifies code switching between English (ENG) a number of Pacific languages:

Acehnese	ace

Buginese	bug

Cebuano	ceb
Chamorro	cha
Chuukese	chk
Fijian	fij
Gilbertese	gil
Hawaiian	haw
Hiligaynon	hil
Hiri Motu	hmo
Ilocano	ilo
Javanese	jav
Marshallese	mah
Malagasy	mlg
Māori	mri
Malay	msa
Niuean	niu
Pangasinan	pag
Pohnpeian	pon
Cook Islands Māori	rar
Samoan	smo
Sundanese	sun
Tahitian	tah
Tagalog	tgl
Tonga	ton
Tuvaluan	tvl
Waray	war
Wallisian	wls
Yapese	yap

# Usage

Import and initialize the package:

	from pacific_CodeSwitch import LID
	LID = LID(language = "mri", algorithm = "v2")
	
Given a string, get the prediction for each word:

	words, overall = LID.predict(line)
	
# Example Output

[('more', eng), ('jobs', eng), ('in', eng), ('northland', eng), ('he', eng), ('mahi', mri), ('ano', mri), ('kia', mri), ('ora', mri), ('whanau', mri)]
	
# Installation

	pip install git+https://github.com/jonathandunn/pacific_CodeSwitch.git
