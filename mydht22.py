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
                file.write("\"Zeit in JHR-MNT-TAG,"
                           "STD:MIN\";\"MaxBeschlSeitLetztemEintragX\";\"MinBeschlSeitLetztemEintragX"
                           "\";\"MaxBeschlSeitLetztemEintragY\";\"MinBeschlSeitLetztemEintragY"
                           "\";\"MaxBeschlSeitLetztemEintragZ\";\"MinBeschlSeitLetztemEintragZ"
                           "\";\"AnzahlGemessenerWerte\"\n")
                file.close()

        # go now into the main-program:
        print("Die Beschleunigungsdaten und die Temperaturwerte werden nun im Minutentakt in die "
              "angegebenen Dateien gespeichert.")
        print("Zum Beenden des Programms drücken Sie Str+C.\n")
        numOfAccSamples = 0  # we store that to know how many samples went into the min/max-variables of acceleration
        timeOfLastMemorySaveAcc = 0  # only every minute the data gets written into memory
        timeOfLastMemorySaveTemp = 0  # only every minute the data gets written into memory
        minMaxAcc = [-10000, -10000, -10000, 10000, 10000, 10000]  # maxAccX, maxAccY, maxAccZ, minAccX, minAccY, minAccZ
        while True:
            # sample the acceleration max/min:
            numOfAccSamples += 1
            accSample = accelerometer.acceleration
            if accSample[0] > minMaxAcc[0]:  # maxAccX
                minMaxAcc[0] = accSample[0]
            elif accSample[0] < minMaxAcc[3]:  # minAccX
                minMaxAcc[3] = accSample[0]
            if accSample[1] > minMaxAcc[1]:  # maxAccY
                minMaxAcc[1] = accSample[1]
            elif accSample[1] < minMaxAcc[4]:  # minAccY
                minMaxAcc[4] = accSample[1]
            if accSample[2] > minMaxAcc[2]:  # maxAccZ
                minMaxAcc[2] = accSample[2]
            elif accSample[2] < minMaxAcc[5]:  # minAccZ
                minMaxAcc[5] = accSample[2]

            # save acceleration data into memory:
            if time.time() - timeOfLastMemorySaveAcc >= 60:
                timeString = datetime.now().strftime("\"%Y-%m-%d,%H:%M\";")
                noErrorOccurredAcc = True
                try:  # save acceleration-data
                    accString = "\"" + str(minMaxAcc[0]) + "\";\"" + str(minMaxAcc[3]) + "\";\"" + str(minMaxAcc[1])\
                                + "\";\"" + str(minMaxAcc[4]) + "\";\"" + str(minMaxAcc[2]) + "\";\"" + str(minMaxAcc[5])\
                                + "\";\"" + str(numOfAccSamples) + "\"\n"
                    accString = accString.replace(".", ",")  # for excel-reasons they need to be replaced
                    fileADX = open(filePathADX, 'a')
                    fileADX.write(str(timeString) + accString)
                    fileADX.close()
                except Exception as error:
                    noErrorOccurredAcc = False
                    print(error.args[0])
                    fileADX.close()
                    pass
                if noErrorOccurredAcc:  # only if the value got really stored we wait for another minute
                    numOfAccSamples = 0
                    minMaxAcc = [0, 0, 0, 10000, 10000, 10000]
                    timeOfLastMemorySaveAcc = time.time()

            # save temperature data into memory:
            if time.time() - timeOfLastMemorySaveTemp >= 60:
                noErrorOccurredTemp = True
                try:  # save temperature-data
                    temperature = sensor.temperature
                    humidity = sensor.humidity
                    fileDHT = open(filePathDHT, 'a')
                    fileDHT.write(
                        str(timeString) + "\"" + str(temperature).replace(".", ",") + "\";\"" + str(humidity).replace(
                            ".", ",") + "\"\n")
                    fileDHT.close()
                except Exception as error:
                    noErrorOccurredTemp = False
                    print(error.args[0])
                    sensor.exit()
                    fileDHT.close()
                    pass
                if noErrorOccurredTemp:  # only if the value got really stored we wait for another minute
                    timeOfLastMemorySaveTemp = time.time()


if __name__ == '__main__':
    main()
