
def convertir_comando(comando):
    COMANDO =""
    if "MFL" in comando[0:3]: #Fluke 8845/fluke45
        COMANDO+="mul "
        if "Volt" in comando:
            if "DC" in comando:
                if "Range" in comando:
                    if "1" in  comando:
                        COMANDO+="--run voltage --DCAC DC --range 1"
                    elif "2" in comando:
                        COMANDO+="--run voltage --DCAC DC --range 2"
                    elif "3" in comando:
                        COMANDO+="--run voltage --DCAC DC --range 3"
                    elif "4" in comando:
                        COMANDO+="--run voltage --DCAC DC --range 4"
                    elif "5" in comando:
                        COMANDO+="--run voltage --DCAC DC --range 5"
                    else:
                        pass
            elif "AC" in comando:
                if "Range" in comando:
                    if "1" in  comando:
                        COMANDO+="--run voltage --DCAC AC --range 1"
                    elif "2" in comando:
                        COMANDO+="--run voltage --DCAC AC --range 2"
                    elif "3" in comando:
                        COMANDO+="--run voltage --DCAC AC --range 3"
                    elif "4" in comando:
                        COMANDO+="--run voltage --DCAC AC --range 4"
                    elif "5" in comando:
                        COMANDO+="--run voltage --DCAC AC --range 5"
                    else:
                        pass
        if "Current" in comando:
            if "DC" in comando:
                if "Range" in comando:
                    if "1" in  comando:
                        COMANDO+="--run current --DCAC DC --range 1"
                    elif "2" in comando:
                        COMANDO+="--run current --DCAC DC --range 2"
                    elif "3" in comando:
                        COMANDO+="--run current --DCAC DC --range 3"
                    elif "4" in comando:
                        COMANDO+="--run current --DCAC DC --range 4"
                    elif "5" in comando:
                        COMANDO+="--run current --DCAC DC --range 5"
                    else:
                        pass
            elif "AC" in comando:
                if "Range" in comando:
                    if "1" in  comando:
                        COMANDO+="--run current --DCAC AC --range 1"
                    elif "2" in comando:
                        COMANDO+="--run current --DCAC AC --range 2"
                    elif "3" in comando:
                        COMANDO+="--run current --DCAC AC --range 3"
                    elif "4" in comando:
                        COMANDO+="--run current --DCAC AC --range 4"
                    elif "5" in comando:
                        COMANDO+="--run current --DCAC AC --range 5"
                    else:
                        pass
        if "Resist" in comando:
            if "2Wire" in comando:
                if "Range" in comando:
                    if "1" in  comando:
                        COMANDO+="--run resistance --range 1"
                    elif "2" in comando:
                        COMANDO+="--run resistance --range 2"
                    elif "3" in comando:
                        COMANDO+="--run resistance --range 3"
                    elif "4" in comando:
                        COMANDO+="--run resistance --range 4"
                    elif "5" in comando:
                        COMANDO+="--run resistance --range 5"
                    elif "6" in comando:
                        COMANDO+="--run resistance --range 6"
                    elif "7" in comando:
                        COMANDO+="--run resistance --range 7"
                    else:
                        pass
            if "4Wire" in comando:
                if "Range" in comando:
                    if "1" in  comando:
                        COMANDO+="--run resistance --4H true --range 1"
                    elif "2" in comando:
                        COMANDO+="--run resistance --4H true --range 2"
                    elif "3" in comando:
                        COMANDO+="--run resistance --4H true --range 3"
                    elif "4" in comando:
                        COMANDO+="--run resistance --4H true --range 4"
                    elif "5" in comando:
                        COMANDO+="--run resistance --4H true --range 5"
                    elif "6" in comando:
                        COMANDO+="--run resistance --4H true --range 6"
                    elif "7" in comando:
                        COMANDO+="--run resistance --4H true --range 7"
                    else:
                        pass
        if "DIODE" in comando:
            COMANDO+="--run diode"
        if "FREQ" in comando:
            if "Range" in comando:
                if "1" in  comando:
                    COMANDO+="--run frecuency --range 1"
                elif "2" in comando:
                    COMANDO+="--run frecuency --range 2"
                elif "3" in comando:
                    COMANDO+="--run frecuency --range 3"
                elif "4" in comando:
                    COMANDO+="--run frecuency --range 4"
    elif "FAE" in comando[0:3]: #Protek/array
        COMANDO+="PSU "
        if "FAESETLIMI" in comando: #SETEA EL LIMETE DE CORRIENTE
            value = comando.split("FAESETLIMI")[1]
            COMANDO+=f"--set current={value} --on true"
        elif "FAEON": #ENCIENDE LA FUENTE
            COMANDO+="--on true"
        elif "FAEOFF": #APAGA LA FUENTE
            COMANDO+="--off true"
        elif "FAESETVOLT" in comando:
            value = comando.split("FAESETVOLT")[1]
            COMANDO+=f"--set volt={value} --on true"
        elif "FAEREAD_AMPI" in comando:
            COMANDO+=f"--get current=True"
        elif "FAEREAD_VOLT" in comando:
            COMANDO+=f"--get volt=True"
        elif "FAEREAD_POT" in comando:
            COMANDO+=f"--get power=True"
    elif "PS8" in comando[0:3]: #Prosim 8
        COMANDO = "PS8 "
        #COMANDOS RELACIONADOS AL ECG
        if "NSB" in comando: #setear Normal Sinus rate
            rate = comando.split("NSB")[1]
            COMANDO+=f"--run ECG --frec {rate}"
        elif "NSA" in comando: #Setea amplitud
            amplitud = comando.split("NSA")[1]
            COMANDO+=f"--run ECG --amp {amplitud}"
        elif "SIN" in comando: #Setea una onda sinusoidal
            rate = comando.split("SIN")[1]
            COMANDO+=f"--run SIN --frec {rate}"
        elif "STD" in comando: #Desviacion STkey 
            if "0.1" in comando:#Desviacion 0.1
                COMANDO+=f"--run ECG --dev 0.10"
            else: #Solo tiene estas 2 desviaciones al parecer
                COMANDO+=f"--run ECG --dev 0.00"
        elif "PVC" in comando: #Premature Ventricular contraction
            COMANDO+=f"--run PreVentricular --arritmia PVC"
        elif "NCP" in comando: #Pacemaker waveform = NONC (sin captura)
            COMANDO+=f"--run pacer --wave SinCaptura"
        elif "NFU" in comando: #Pacemaker waveform = NONF (sin Funcion)
            COMANDO+=f"--run pacer --wave SinFuncion"
        elif "VH+20" in comando: #Pacemaker amplitud ventriculo 20
            COMANDO+=f"--run pacer --amplitud 020 --chamber V --polaridad P"
        elif "VW0.1" in comando: #Pacemaker ancho 0.1ms
            COMANDO+=f"--run pacer --width 0.1 --chamber V --polaridad P"
        elif "AH+2" in comando: #Pacemaker amplitud atrial 2mv
            COMANDO+=f"--run pacer --amplitud 002 --chamber A --polaridad P"
        elif "AH-2" in comando: #Pacemaker amplitud atrial -2mv
            COMANDO+=f"--run pacer --amplitud 002 --chamber A --polaridad N"
        elif "SQU" in comando:
            COMANDO +="--run cuadrada --frec 2"
        elif "ZERO" in comando:
            COMANDO +="--run asistolia"
            
        #SpO2
        elif "SAT" in comando:
            saturacion = comando.split("=")[1]
            COMANDO +=f"--run SPO2 --saturacion {saturacion}"
        elif "PERF" in comando:
            perfusion = comando.split("=")[1]
            COMANDO +=f"--run SPO2 --perfusion {perfusion}"
        elif "TYPE" in comando:
            tipo = comando.split("=")[1]
            COMANDO +=f"--run SPO2 --sensor {tipo}"
            
        #RESPIRATORIA
        elif "RESPLEAD" in comando:
            lead = comando.split("=")[1]
            COMANDO +=f"--run RESP --lead {lead}"
        elif "RR" in comando:
            frec = comando.split("RR")[1]
            COMANDO +=f"--run RESP --frec {frec}"
        elif "RESPBASE" in comando:
            base = comando.split("=")[1]
            COMANDO +=f"--run RESP --baseline {base}"
        elif "RO" in comando:
            amp = comando.split("RO")[1]
            COMANDO +=f"--run RESP --amp {amp}"
        
        #PRESION INVASIVA
        elif "P1S" in comando:
            presion = comando.split("P1S")[1]
            COMANDO +=f"--run PI --static {presion} --ch 1"
        elif "P2S" in comando:
            presion = comando.split("P2S")[1]
            COMANDO +=f"--run PI --static {presion} --ch 2"
        elif "ART" in comando:
            if "P1" in comando:
                COMANDO +=f"--run PI --wave arterial --ch 1"
            elif "P2" in comando:
                COMANDO +=f"--run PI --wave arterial --ch 2"
        elif "LV" in comando:
            if "P1" in comando:
                COMANDO +=f"--run PI --wave ventriculoizquierdo --ch 1"
            elif "P2" in comando:
                COMANDO +=f"--run PI --wave ventriculoizquierdo --ch 2"
        elif "RV" in comando:
            if "P1" in comando:
                COMANDO +=f"--run PI --wave ventriculoderecho --ch 1"
            elif "P2" in comando:
                COMANDO +=f"--run PI --wave ventriculoderecho --ch 2"
        #Falta todo lo relacionado al control
        #PRESION NO INVASIVA
        elif "ADAMS-" in comando: #PNI ADULTO
            if "255/195" in comando:
                if "envshift=-2" in comando:
                    COMANDO +="--run pni --afrec 80 --dinamica 255/195 --envolvente -2 --vol 1.0" 
                else:
                    COMANDO +="--run pni --afrec 80 --dinamica 255/195 --vol 1.0" 
            elif "120/80" in comando:
                COMANDO +="--run pni --afrec 80 --dinamica 120/80 --vol 1.0" 
            elif "60/30" in comando:
                if "hr=120" in comando:
                    COMANDO +="--run pni --afrec 120 --dinamica 60/30 --vol 1.0"
                elif "hr=80" in comando:
                    if "envshift=-1" in comando:
                        COMANDO +="--run pni --afrec 80 --dinamica 60/30 --vol 1.0 --envolvente -1"
                    else:
                        COMANDO +="--run pni --afrec 80 --dinamica 60/30 --vol 1.0"
        elif "MKARM40" in comando:
            COMANDO +="--run pni --afrec 80 --dinamica 120/80 --vol 1.0" #Es exactamente igual no se por que sera
        elif "ADAMSNEO-" in comando: #PNI NEO
            if "120/80" in comando:
                COMANDO +="--run pni --nfrec 120 --dinamica 120/80 --vol 1.0"
            elif "100/60" in comando:
                if "envshift=-2" in comando:
                    COMANDO +="--run pni --nfrec 120 --dinamica 100/60 --vol 1.0 --envolvente -2"
                else:
                    COMANDO +="--run pni --nfrec 120 --dinamica 100/60 --vol 1.0"
            elif "60/30" in comando:
                COMANDO +="--run pni --nfrec 120 --dinamica 60/30 --vol 1.0"
    return COMANDO
        