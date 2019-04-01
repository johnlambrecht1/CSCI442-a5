package com.example.a442servertts;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.speech.tts.TextToSpeech;
import android.speech.tts.Voice;
import android.util.Log;
import android.widget.Toast;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public class TTS extends Thread implements
        TextToSpeech.OnInitListener  {

    private TextToSpeech tts;
    private Context context;
    public Handler handler;
    private String last;

    public TTS(Context con){
        tts = tts = new TextToSpeech(con, this);
        con = context;
        last = "c";
        Set<String> a = new HashSet<>();
        a.add("male");
        Voice v = new Voice("en-us-x-sfg#male_2-local",new Locale("en","US"),400,200,true,a);
        tts.setVoice(v);

    }

    public void run()
    {
        Looper.prepare();
        handler = new Handler(){
            public void handleMessage(Message msg) {
                String aResponse = msg.getData().getString("LM");
                speakOut(aResponse);

            }
        };
        Looper.loop();
    }

    @Override
    public void onInit(int status) {
        // TODO Auto-generated method stub

        if (status == TextToSpeech.SUCCESS) {

            int result = tts.setLanguage(Locale.US);

            //tts.setPitch(5); // set pitch level

            //tts.setSpeechRate(2); // set speech speed rate

            if (result == TextToSpeech.LANG_MISSING_DATA
                    || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                Toast.makeText(context, "Language is not supported", Toast.LENGTH_SHORT).show();
            }

        } else {
            Toast.makeText(context, "Initilization Failed", Toast.LENGTH_SHORT).show();

        }

    }


    public void speakOut(String text) {
        Log.v("LOGGING SPEECH", "text: " + text);
        //String text = txtText.getText().toString();
        if(last != text) {
            last = text;
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null);
            while (tts.isSpeaking()) {
                try {
                    Thread.sleep(200);
                } catch (Exception e) {
                }
            }
        }

    }
}


