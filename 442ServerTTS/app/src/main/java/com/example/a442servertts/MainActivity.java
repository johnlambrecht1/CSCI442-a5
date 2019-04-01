package com.example.a442servertts;

import android.content.Context;
import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.Enumeration;

public class MainActivity extends AppCompatActivity {

    public TextView tv;
    NetworkConnectionThread nct;
    public static Context context;
    private static TTS tts;
    public TextView cmdText;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        context = this;

        ///show IP address for connection
        tv = (TextView) findViewById(R.id.ipTextView);
        tv.setText("boogied " ); //getIpAddress());
        cmdText = (TextView) findViewById(R.id.cmdText);
        cmdText.setText(getIpAddress());
        //Button sendButton = (Button) findViewById(R.id.sendButton);
        //sendButton.setOnClickListener(this);
        ///Start network thread / server listening for connnection
      nct = NetworkConnectionThread.getInstance();
        nct.setParent(this);
        nct.start();

        tts = new TTS(this);
        tts.start();
    }
    @Override
    protected void onDestroy() {
        tts = null;
    }

    public static String getIpAddress() {
        String ipAddress = "Unable to Fetch IP......";
        try {
            Enumeration en;

            en = NetworkInterface.getNetworkInterfaces();

            while ( en.hasMoreElements()) {
                Log.v("LOGGING", "has Elements*****************");
                NetworkInterface intf = (NetworkInterface)en.nextElement();
                for (Enumeration enumIpAddr = intf.getInetAddresses(); enumIpAddr.hasMoreElements();) {

                    InetAddress inetAddress = (InetAddress)enumIpAddr.nextElement();
                    if (!inetAddress.isLoopbackAddress()&&inetAddress instanceof Inet4Address) {

                        ipAddress=inetAddress.getHostAddress();
                        return ipAddress;
                    }
                }
            }
        } catch (SocketException ex) {
            ex.printStackTrace();
        }
        return ipAddress;
    }

    public final static Handler handler = new Handler() {

        public void handleMessage(Message msg) {
            String aResponse = msg.getData().getString("client");

            //int choice = new Integer(aResponse);
            Message sendMsg = tts.handler.obtainMessage();
            Bundle b = new Bundle();
            sendMsg.setData(b);
            tts.handler.sendMessage(sendMsg);
            //switch (choice) {
               // case 0:
                    sendMsg = tts.handler.obtainMessage();
                    b = new Bundle();
                    b.putString("LM", aResponse);
                    sendMsg.setData(b);
                    tts.handler.sendMessage(sendMsg);
                   // break;

            //}

        }
    };
}
