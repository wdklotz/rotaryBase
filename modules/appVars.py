# -*- coding: utf-8 -*-

# class AppVars:
	# items = dict (
		# version = "rotaryBase3v0.3u4",
		# title   = "Rotary Intl. Gréoux-les-Bains",
        # r_blue  = "#4BABE8"
		# )
# version text
def version():
    with open("applications/rotaryBase_grid_repository/VERSION.txt","r") as file:
        data = file.read()
    return data

