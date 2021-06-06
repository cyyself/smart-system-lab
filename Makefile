run: mainui.py db.sqlite
	python3 gui.py
mainui.py: main.ui
	pyuic5 -o mainui.py main.ui
db.sqlite: db_init.py
	python3 db_init.py
clean:
	rm db.sqlite
	rm mainui.py