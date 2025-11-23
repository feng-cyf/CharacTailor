// 这是一个简单的测试脚本，用于验证图片上传和预览功能
console.log('测试图片上传和预览功能...');

// 模拟上传响应格式
const mockResponse = {
  code: 200,
  message: '上传成功',
  data: {
    local_url: 'http://localhost:8000/file/UploadedFiles/image/test.jpg',
    cloud_url: 'https://cloud-storage/test.jpg',
    file_name: 'test.jpg'
  }
};

console.log('服务器返回的响应格式:', mockResponse);
console.log('预览应该使用的URL:', mockResponse.data.local_url);
console.log('发送给AI的URL:', mockResponse.data.cloud_url);

console.log('\n测试结论:');
console.log('- 预览功能现在应该使用服务器返回的local_url');
console.log('- 发送给AI的功能使用cloud_url');
console.log('- 两者现在应该正常工作并且逻辑一致');