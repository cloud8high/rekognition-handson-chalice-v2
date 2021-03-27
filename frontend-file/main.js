let app = new Vue({
  el: '#app',
  data: {
      imageFile: '',
      imagePreview: '',
      celebrityInfo: '',
      isLoading: false,
  },
  methods: {
      onChange: function(event) {
          this.celebrityInfo = '';
          this.imageFile = event.target.files[0];
          if (this.imageFile && this.imageFile.type.match(/^image\/(png|jpeg)$/)) {
              this.imagePreview = window.URL.createObjectURL(this.imageFile);
          }
      },
      onSubmit: function(event) {
          this.isLoading = true;
          this.celebrityInfo = '';
          const targetUrl = '** API Gateway URL をここに貼り付け! **';
          const formData = new FormData();
          formData.append('uploadfile', this.imageFile);
          var config = {
              headers: {
                  'content-type': 'multipart/form-data',
              }
          };
          const that = this;
          axios
              .post(targetUrl, formData, config)
              .then(response => {
                  that.celebrityInfo = response.data;
              })
              .catch(error => {
                  console.error(error);
                  that.celebrityInfo = {errorMessage: '画像から有名人を認識できませんでした。他の画像に変更してください。'}
              })
              .finally(() => {
                  that.isLoading = false;
              });
      }
  }
})