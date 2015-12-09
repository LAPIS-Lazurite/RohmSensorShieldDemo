/* FILE NAME: rohm_sensor.c
 * The MIT License (MIT)
 * 
 * Copyright (c) 2015  Lapis Semiconductor Co.,Ltd.
 * All rights reserved.
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
*/

#define SUBGHZ_CH			36
#define SUBGHZ_PANID		0xABCD
#define SUBGHZ_GATEWAY		0xAC8E
#define SUBGHZ_BITRATE		SUBGHZ_100KBPS
#define SUBGHZ_PWR			SUBGHZ_PWR_1MW


#define BLUE_LED			26
#define ORANGE_LED			25

#define DEBUG

unsigned char tx_data[128];

void setup(void)
{
	byte rc;
	// initializing peripherals
	Serial.begin(115200);
	SubGHz.init();
	Wire.begin();
	
	pinMode(BLUE_LED,OUTPUT);
	pinMode(ORANGE_LED,OUTPUT);
	
	
	// initializing sensor
	rpr0521rs.init();
	rc = bm1423.init(0);
	rc = bm1383.init(0);
	rc = kxg03.init(0);
	ml8511.init(A0);
	
	// Initializing SensorGraph tool
	SubGHz.begin(SUBGHZ_CH,SUBGHZ_PANID,SUBGHZ_BITRATE,SUBGHZ_PWR);
	
	// Reset Graph tool
	Print.init(tx_data,sizeof(tx_data));
	Print.p("SensorReset");
	digitalWrite(BLUE_LED, LOW);
	SubGHz.send(SUBGHZ_PANID,SUBGHZ_GATEWAY,tx_data,Print.len(),NULL);
	digitalWrite(BLUE_LED, HIGH);
	Serial.print(tx_data);
	sleep(10);
	
	// Set Sensor
	Print.init(tx_data,sizeof(tx_data));
	Print.p("SensorList,RPR0521-ALS,1,RPR0521-PS,1,BM1423-MAG,3,BM1383-T,1,BM1383-P,1,KXG03-G,3,KXG03-A,3,ML8511-UV,1,");
	digitalWrite(BLUE_LED, LOW);
	SubGHz.send(SUBGHZ_PANID,SUBGHZ_GATEWAY,tx_data,Print.len(),NULL);
	digitalWrite(BLUE_LED, HIGH);
	digitalWrite(ORANGE_LED,LOW);
//	Serial.print(tx_data);
	digitalWrite(ORANGE_LED,HIGH);
	SubGHz.close();
}

void loop(void)
{
	SUBGHZ_MSG msg;
	float fval[6];
	unsigned short usval[1];
	
	Print.init(tx_data,sizeof(tx_data));
	Print.p("SensorData,");
	
	// get from rpr0521rs
	rpr0521rs.get_psalsval(usval,fval);
	Print.f(fval[0],0);						// ALS
	Print.p(",");
	Print.l(usval[0],DEC);					// PS
	Print.p(",");
	
	// get from BM1423
	bm1423.get_val(fval);
	Print.f(fval[0],2);						// ALS
	Print.p(",");
	Print.f(fval[1],2);						// ALS
	Print.p(",");
	Print.f(fval[2],2);						// ALS
	Print.p(",");

	// get from BM1423
	bm1383.get_temppressval(&fval[0],&fval[1]);
	Print.f(fval[0],2);						// ALS
	Print.p(",");
	Print.f(fval[1],2);						// ALS
	Print.p(",");

	// get from KXG03
	kxg03.get_val(fval);
	Print.f(fval[0],2);						// ALS
	Print.p(",");
	Print.f(fval[1],2);						// ALS
	Print.p(",");
	Print.f(fval[2],2);						// ALS
	Print.p(",");
	Print.f(fval[3],2);						// ALS
	Print.p(",");
	Print.f(fval[4],2);						// ALS
	Print.p(",");
	Print.f(fval[5],2);						// ALS
	Print.p(",");

	// get from ML8511
	ml8511.get_val(fval);
	Print.f(fval[0],2);						// ALS
	Print.p(",");
	
	// send subghz
	SubGHz.begin(SUBGHZ_CH,SUBGHZ_PANID,SUBGHZ_BITRATE,SUBGHZ_PWR);
	digitalWrite(BLUE_LED, LOW);
	#ifdef DEBUG
	Serial.print("START SENDING\t");
	Serial.print_long(millis(),DEC);
	Serial.println("");
	#endif
	msg=SubGHz.send(SUBGHZ_PANID,SUBGHZ_GATEWAY,tx_data,Print.len(),NULL);
	Serial.print("msg=");
	Serial.print_long(msg,DEC);
	Serial.print("\r\n");	
	#ifdef DEBUG
	Serial.print("END SENDING\t");
	Serial.print_long(millis(),DEC);
	Serial.println("");
	#endif
	digitalWrite(BLUE_LED, HIGH);
	SubGHz.close();
	
	// Send Serial
	digitalWrite(ORANGE_LED,LOW);
	Serial.print(tx_data);
	digitalWrite(ORANGE_LED,HIGH);
	Serial.println("");
	#ifdef DEBUG
	Serial.print("BEFORE DELAY\t");
	Serial.print_long(millis(),DEC);
	Serial.println("");
	#endif
	sleep(100);
	#ifdef DEBUG
	Serial.print("END DELAY\t");
	Serial.print_long(millis(),DEC);
	Serial.println("");
	#endif
}

