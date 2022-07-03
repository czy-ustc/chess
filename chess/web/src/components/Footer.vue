<template>
  <el-footer id="footer">
    <div id="contact">
      <i class="el-icon-phone-outline"></i>
      Tel:19159079196
      <el-divider direction="vertical"></el-divider>
      <i class="el-icon-message"></i>
      Email:chenzhiyuan@mail.ustc.edu.cn
    </div>
  </el-footer>
</template>

<script>

export default {
  name: 'Footer',
  components: {
  },
  data () {
    return {
    };
  },
  methods: {
  }
}
</script>

<style scoped>
#footer {
  left: 0;
  bottom: 0;
  height: 70px;
  width: 100%;
  margin: auto;
  text-align: center;
  font-family: Georgia;
  border-width: 3px 0px 0px 0px;
  border-style: solid;
  border-color: #dcdfe6;
  position: fixed;
}
#contact {
  margin-top: 20px;
}
.el-footer {
  background-color: #dcdfe6;
  padding: 0;
}
</style>