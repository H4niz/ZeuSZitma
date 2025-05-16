# Documentation Index - Zitmo Research Project

Chào mừng đến với tài liệu dự án nghiên cứu Zitmo. Đây là hướng dẫn toàn diện về hệ thống mô phỏng malware banking cho mục đích giáo dục.

## 📚 Tài liệu có sẵn

### 1. [Kiến trúc hệ thống](architecture.md)
Mô tả chi tiết về kiến trúc tổng thể của hệ thống, bao gồm:
- Sơ đồ kiến trúc
- Các thành phần server và client
- Luồng dữ liệu
- Database schema
- Giao thức giao tiếp

### 2. [API Reference](api_reference.md)
Tài liệu tham khảo đầy đủ về các API endpoints:
- Client APIs (register, ping, report)
- Admin APIs (devices, commands, SMS)
- Request/Response formats
- Error codes
- Code examples

### 3. [Phân tích bảo mật](security_analysis.md)
Phân tích chi tiết về các khía cạnh bảo mật:
- Attack vectors
- Vulnerability analysis
- Detection methods
- Mitigation strategies
- Educational value

### 4. [Hướng dẫn triển khai](deployment_guide.md)
Hướng dẫn từng bước để triển khai hệ thống:
- Yêu cầu môi trường
- Network setup
- Server installation
- Client deployment
- Testing procedures

### 5. [Xử lý sự cố](troubleshooting.md)
Giải pháp cho các vấn đề thường gặp:
- Server issues
- Client problems
- Network errors
- Performance optimization
- Recovery procedures

## 🚀 Bắt đầu nhanh

### Cho người mới
1. Đọc [README chính](../README.md) để hiểu tổng quan
2. Xem [Kiến trúc hệ thống](architecture.md)
3. Làm theo [Hướng dẫn triển khai](deployment_guide.md)

### Cho developers
1. Tham khảo [API Reference](api_reference.md)
2. Xem [Security Analysis](security_analysis.md)
3. Debug với [Troubleshooting Guide](troubleshooting.md)

### Cho researchers
1. Nghiên cứu [Security Analysis](security_analysis.md)
2. Xem [Architecture](architecture.md) để hiểu cách hoạt động
3. Tham khảo [BRD](../BRD.md) cho technical analysis

## 📋 Checklists

### Pre-deployment Checklist
- [ ] Chuẩn bị môi trường lab isolated
- [ ] Cài đặt dependencies
- [ ] Configure network settings
- [ ] Test connectivity
- [ ] Review security measures

### Post-deployment Checklist
- [ ] Verify all services running
- [ ] Test basic functionality
- [ ] Check logs for errors
- [ ] Confirm data flow
- [ ] Document any issues

### Security Checklist
- [ ] Network isolation confirmed
- [ ] Firewall rules in place
- [ ] Access controls set
- [ ] Monitoring enabled
- [ ] Backup configured

## ⚠️ Lưu ý quan trọng

1. **Mục đích giáo dục**: Hệ thống này CHỈ dành cho nghiên cứu và giáo dục
2. **Môi trường an toàn**: Luôn chạy trong lab environment isolated
3. **Tuân thủ pháp luật**: Không sử dụng cho mục đích bất hợp pháp
4. **Có giám sát**: Luôn có supervision khi sử dụng
5. **Xóa sau khi dùng**: Clean up toàn bộ sau khi hoàn thành

## 🔗 Tài nguyên bổ sung

### Internal Links
- [Source Code - Server](../server/)
- [Source Code - Client](../EduZitmo/)
- [Technical Analysis](../BRD.md)
- [Main README](../README.md)

### External Resources
- [Android Security Documentation](https://source.android.com/security)
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 📝 Đóng góp tài liệu

Để cải thiện tài liệu:

1. Fork repository
2. Tạo branch mới
3. Thực hiện thay đổi
4. Submit pull request

### Quy tắc viết tài liệu
- Sử dụng Markdown format
- Thêm code examples
- Include diagrams where helpful
- Keep language clear and concise
- Update table of contents

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2023-12-01 | Initial documentation |
| 1.1 | 2023-12-15 | Added troubleshooting guide |
| 1.2 | 2024-01-01 | Updated API reference |

## 📞 Support

Nếu cần hỗ trợ:
- Email: haniz.cons@gmail.com
- GitHub Issues: [Create Issue](https://github.com/yourusername/ZeuSZitma/issues)
- Documentation: [Wiki](https://github.com/yourusername/ZeuSZitma/wiki)

---

**Remember**: Sử dụng kiến thức này một cách có trách nhiệm và chỉ cho mục đích giáo dục! 🎓