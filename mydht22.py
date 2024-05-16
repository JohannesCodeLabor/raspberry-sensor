import time
import board
import busio
import adafruit_dht
import adafruit_adxl34x
from datetime import datetime


def main():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
    except Exception as error:
        print("Fehler bei Zugriff auf I2C-Schnittstelle. "
              "Aktivieren Sie \"I2C\" unter: Einstellungen->Raspberry Pi-Konfiguration->Schnittstellen")
    accelerometer = adafruit_adxl34x.ADXL345(i2c)
    sensor = adafruit_dht.DHT22(board.D4)
    filePathDHT = ""
    filePathADX = ""
    dhtDefined = False
    adxDefined = False
    while True:
        if not dhtDefined:
            print("Konfiguriere DHT22:")
            choiceDHT = input(
                "Sollen die Daten vom DHT22 in eine neue Datei gespeichert werden(1) oder in eine bereits bestehende("
                "2)? (1/2)")
            if choiceDHT != "1" and choiceDHT != "2":
                print("Geben Sie entweder 1 oder 2 ein.")
                continue

            filePathDHT = input("Dateipfad für DHT?\n")
            try:  # check if its a correct path:
                fileTypeBeginIndex = filePathDHT.find(".")
                if fileTypeBeginIndex == -1:
                    filePathDHT += ".csv"
                else:
                    filePathDHT = filePathDHT[:fileTypeBeginIndex] + ".csv"
                file = open(filePathDHT, 'w')
                file.close()
                dhtDefined = True  # only gets activated when no error occurred until here
            except Exception as error:
                print(error.args[0])
                continue

            if choiceDHT == "1":
                file = open(filePathDHT, 'w')
                # write the header of the new file:
                file.write("\"Zeit in JHR-MNT-TAG,STD:MIN\";\"Temperatur in °C\";\"Luftfeuchte in %\"\n")
                file.close()

        ########################################################
        if not adxDefined:
            print("Konfiguriere ADXL345:")
            choiceADX = input(
                "Sollen die Daten vom ADXL345 in eine neue Datei gespeichert werden(1) oder in eine bereits "
                "bestehende(2)? (1/2)")
            if choiceADX != "1" and choiceADX != "2":
                print("Geben Sie entweder 1 oder 2 ein.")
                continue

            filePathADX = input("Dateipfad vom ADX?\n")
            try:  # check if its a correct path:
                fileTypeBeginIndex = filePathADX.find(".")
                if fileTypeBeginIndex == -1:
                    filePathADX += ".csv"
                else:
                    filePathADX = filePathADX[:fileTypeBeginIndex] + ".csv"
                file = open(filePathADX, 'w')
                file.close()
                adxDefined = True  # only gets activated when no error ocured until here
            except Exception as error:
                print(error.args[0])
                continue

            if choiceADX == "1":
                file = open(filePathADX, 'w')
                # write the header of the new file:
                file.write("\"Zeit in JHR-MNT-TAG,STD:MIN\";\"BeschleunigungX\";\"BeschleunigungY\";\"BeschleunigungZ"
                           "\"\n")
                file.close()

        # go now into the main-program:
        print("Die Beschleunigungsdaten und die Temperaturwerte werden nun im Minutentakt in die "
              "angegebenen Dateien gespeichert.")
        print("Zum Beenden des Programms drücken Sie Str+C.\n")
        counter = 0
        while True:
            timeString = datetime.now().strftime("\"%Y-%m-%d,%H:%M\";")
            if counter >= 60:  # do every minute:
                counter = 0
                try:  # save acceleration-data
                    accelerationString = "\"%f\";\"%f\";\"%f\"\n" % accelerometer.acceleration
                    fileADX = open(filePathADX, 'a')
                    fileADX.write(str(timeString) + accelerationString.replace(".", ","))
                    fileADX.close()
                except Exception as error:
                    fileADX.close()
                    pass

                try:  # save temperature-data
                    temperature = sensor.temperature
                    humidity = sensor.humidity
                    fileDHT = open(filePathDHT, 'a')
                    fileDHT.write(str(timeString) + "\"" + str(temperature).replace(".", ",") + "\";\"" + str(humidity).replace(".", ",") + "\"\n")
                    fileDHT.close()
                except RuntimeError as error:
                    print("Errors happen fairly often, DHTs are hard to read, just keep going:")
                    print(error.args[0])
                except Exception as error:
                    sensor.exit()
                    fileDHT.close()
                    pass
            counter += 1
            time.sleep(1.0)  # wait for a minute


if __name__ == '__main__':
    main()
