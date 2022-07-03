<template>
  <div>
    <Header />
    <el-container>
      <el-main>
        <article
          class="markdown-body"
          v-html="article"
        >
        </article>
      </el-main>
      <el-aside>
        <div id="catalogue">
          <div style="margin:0px 0 20px 180px;font-size:18px;font-weight:bold;">目录</div>
          <el-scrollbar max-height="350px">
            <el-tabs
              @tab-click="handleClick"
              v-model="activeName"
              tab-position="right"
              style="height: auto;"
            >
              <el-tab-pane
                :name="'tab'+index"
                :class="item.lev"
                v-for="(item, index) in navList"
                :key="index"
                :label="item.name"
              ></el-tab-pane>
            </el-tabs>
          </el-scrollbar>
        </div>
      </el-aside>
    </el-container>
    <Footer />
  </div>
</template>

<script>
import axios from 'axios'
import 'github-markdown-css/github-markdown.css'

import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'Rule',
  components: {
    Header,
    Footer,
  },
  data: function () {
    return {
      article: '',
      scroll: '',
      navList: [],
      activeName: 'tab0',
    }
  },
  mounted: async function () {
    let res = await axios.get('/article/')
    this.article = res.data
    setTimeout(() => {
      this.init()
    }, 100)
    window.addEventListener('scroll', this.dataScroll)

    setTimeout(() => {
      let imgs = document.querySelectorAll('img')
      for (let i = 1; i < imgs.length; i++) {
        imgs[i].style.width = '25%'
        imgs[i].style.position = 'relative'
        imgs[i].style.left = '30%'
        imgs[i].style.marginBottom = '20px'
      }
    }, 200)

  },
  methods: {
    handleClick: function (tab) {
      this.jump(tab.index)
    },
    dataScroll: function () {
      this.scroll = document.documentElement.scrollTop || document.body.scrollTop
    },
    jump: function (index) {
      let jump_ = Array.from(document.querySelectorAll("h1, h2, h3, h4, h5, h6")).slice(1)
      let total = jump_[index].offsetTop - 80
      document.body.scrollTop = total
      document.documentElement.scrollTop = total
      window.pageYOffset = total
    },
    loadScroll: function () {
      let self = this
      for (var i = self.navList.length - 1; i >= 0; i--) {
        if (self.scroll >= self.navList[i].offsetTop - 100) {
          self.activeName = 'tab' + i
          break
        }
      }
    },
    selectAllTitle: function () {
      let title = document.querySelectorAll("h1, h2, h3, h4, h5, h6");

      this.navList = Array.from(title).slice(1);
      this.navList.forEach(item => {
        item.name = item.textContent
      })
      this.navList.forEach(el => {
        let index = el.localName.indexOf('h')
        el.lev = 'lev' + el.localName.substring(index + 1, el.localName.length)
      })
    },
    init: function () {
      this.selectAllTitle()
      this.$nextTick(() => {
        setTimeout(() => {
          let navs = document.querySelectorAll('aside .el-tabs__item');
          for (let i = navs.length - 1; i >= 0; i--) {
            document.querySelector('#' + navs[i].id).style.padding = '0';
            try {
              let lev = this.navList[i].lev;
              document.querySelector('#' + navs[i].id).style['text-align'] = 'left'
              if (lev == 'lev1') {
                document.querySelector('#' + navs[i].id).style.paddingLeft = '20px'
              } else if (lev == 'lev2') {
                document.querySelector('#' + navs[i].id).style.paddingLeft = '35px'
              } else if (lev == 'lev3') {
                document.querySelector('#' + navs[i].id).style.paddingLeft = '50px'
              } else if (lev == 'lev4') {
                document.querySelector('#' + navs[i].id).style.paddingLeft = '65px'
                document.querySelector('#' + navs[i].id).style.fontWeight = '400'
              } else if (lev == 'lev5') {
                document.querySelector('#' + navs[i].id).style.paddingLeft = '80px'
                document.querySelector('#' + navs[i].id).style.fontWeight = '400'
              }
            } catch {
              console.log('error')
            }
          }
        });
      });
    }
  },
  watch: {
    scroll: function () {
      this.loadScroll()
    }
  }
}
</script>

<style scoped>
.el-main {
  margin-top: 30px;
  width: 75%;
}
.markdown-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 45px;
  text-align: left;
}

@media (max-width: 767px) {
  .markdown-body {
    padding: 15px;
  }
}
.el-aside {
  overflow: hidden;
}
#catalogue {
  right: 30px;
  top: 100px;
  width: 300px;
  position: fixed;
}
.icon-sources-wapper.wapper .el-tabs__nav.is-right {
  box-sizing: content-box !important;
}
img {
  max-width: 20%;
}
</style>