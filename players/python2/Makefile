PROGRAM=player
MAIN=player.py
# Note: GnuWin32 version 3.81 sometimes struggles with recursive wildcards (**) 
# unless a shell like bash is present.
PYSOURCES=player.py

all: $(PROGRAM).zip

# We skip the $(PROGRAM) target because chmod doesn't exist on Windows
# and Python files are executed via the python interpreter anyway.

$(PROGRAM).zip:
	@powershell -Command "Compress-Archive -Path $(PYSOURCES) -DestinationPath $(PROGRAM).zip -Force"

clean:
	@powershell -Command "if (Test-Path $(PROGRAM).zip) { Remove-Item $(PROGRAM).zip }"