<template>
  <el-header>
    <el-row id="header_row">
      <el-col
        :span="2"
        id="logo"
      >
        <el-image
          style="height: 40px; margin-top: 8px; "
          src="../../logo.png"
          fit="scale-down"
        ></el-image>
      </el-col>
      <el-col
        :span="6"
        style="text-align: left; margin-left: -25px; user-select: none;"
      >
        <b>量子国际象棋</b>
      </el-col>
      <el-col
        :span="16"
        style="text-align: right"
      >
        <el-space wrap>
          <div
            class="tab"
            @click="jump('/')"
          >
            开始游戏
          </div>
          <div
            class="tab"
            @click="jump('/rule')"
          >
            规则文档
          </div>
          <div
            class="tab"
            @click="jump('https://github.com/czy-ustc/chess')"
          >
            项目地址
          </div>
        </el-space>
      </el-col>
    </el-row>
  </el-header>
</template>

<script>

export default {
  name: 'Header',
  data: function () {
    return {
    }
  },
  methods: {
    jump: function (url) {
      if (url.startsWith('/')) {
        window.location.href = url
      } else {
        window.open(url)
      }
    }
  },
}
</script>

<style scoped>
#header_row {
  margin-bottom: 0;
  height: 62px;
  background-image: linear-gradient(
    to right,
    rgb(80, 227, 249),
    rgb(117, 56, 215)
  );
}
#logo {
  text-align: left;
  padding-left: 30px;
}
.el-header {
  background-color: #fff;
  line-height: 60px;
  height: 60px;
  font-size: large;
  z-index: 10000;
  position: fixed;
  width: 100%;
  top: 0;
  padding: 0;
}
.tab {
  color: rgb(80, 227, 249);
  font-weight: bold;
  font-size: 12px;
  padding: 3px;
  user-select: none;
}
</style>
