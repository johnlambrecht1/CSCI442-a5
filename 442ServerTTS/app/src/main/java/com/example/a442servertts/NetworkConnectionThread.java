package com.example.a442servertts;

import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Log;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * Created by Looney on 4/4/2019.
 */
public class NetworkConnectionThread extends Thread {

    public static NetworkConnectionThread inst;
    public Handler handler;
    public ServerSocket serverSocket;
    static final int SOCKETPORT = 5010;
    public Socket socket;
    public BufferedReader input;
    private MainActivity parent;

    public static NetworkConnectionThread getInstance()
    {
        if(inst == null)
            inst = new NetworkConnectionThread();
        return inst;
    }

    public void setParent(MainActivity c)
    {
        parent = c;
    }

    public void run() {

        //Looper.prepare();
        while (true) {
            if (serverSocket == null) {
                try {

                    serverSocket = new ServerSocket(SOCKETPORT);
                    Log.v("LOGGING", "Server Listening");

                    socket = serverSocket.accept();
                    parent.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            parent.tv.setText("Connected");
                        }
                    });


                } catch (Exception evt) {
                    Log.v("LOGGING", "evt error*****************");
                    evt.printStackTrace();
                }
            }
            if (input == null && serverSocket != null) {
                try {

                    input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream(1024);
                    parent.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            parent.tv.setText("starting to send");

                        }
                    });
                    PrintWriter printwriter = new PrintWriter(socket.getOutputStream(), true);
                    //.write("Please work" +"\n"); // write the message to output stream
                    //printwriter.flush();


                } catch (IOException e) {
                    e.printStackTrace();
                }
            }

            try {


                String command = null;
                if(input != null)
                {
                    parent.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            parent.tv.setText("waiting to read ");

                        }
                    });

                    command = input.readLine();

                    parent.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            parent.tv.setText("recieved ");

                        }
                    });
                    Message msg = parent.handler.obtainMessage();
                    Bundle b = new Bundle();
                    b.putString("client", command);
                    msg.setData(b);
                    parent.handler.sendMessage(msg);
                } else {
                    parent.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            parent.tv.setText("DisConnected");
                            input = null;
                            serverSocket = null;
                        }
                    });

                }
            } catch (IOException e) {
                parent.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        parent.tv.setText("Disconnected");
                    }
                });

            }
        }

        //Looper.loop();

    }

}