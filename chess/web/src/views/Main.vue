<template>
  <div style="background-color: black;">
    <Header />
    <el-main>
      <el-row>
        <el-col :span="8">
          <el-card
            class="box-card"
            :body-style="{ padding: '0px' }"
            v-if="game_start"
          >
            <template #header>
              <div class="card-header">
                <span style="font-weight: bolder; font-size: 24px; color: #6ac8ff; user-select: none;">记录</span>
                <el-button
                  size="large"
                  link
                  class="button"
                  :disabled="logData.length==0"
                  @click="undo"
                >
                  <el-icon
                    :size="20"
                    color="#6ac8ff"
                  >
                    <RefreshLeft />
                  </el-icon>
                </el-button>

              </div>
            </template>

            <el-table
              :data="logData"
              id="log_table"
              style="width: 100%; "
              height="250px"
              empty-text="暂无记录"
              class="log-table"
              :show-header="false"
              :cell-style="{color: 'white', 'background-color': '#152934', border: 'none', 'text-align': 'center'}"
            >
              <el-table-column
                type="index"
                width="40"
              />
              <el-table-column
                prop="white"
                label="白棋"
                width="130"
              />
              <el-table-column
                prop="black"
                label="黑棋"
                width="130"
              />
            </el-table>
            <div class="operation">
              <el-button
                type="info"
                plain
                :disabled="Boolean(game_over)"
                @click="saveDialog = true, chessboard_name = ''"
              >保存</el-button>
              <el-button
                type="info"
                plain
                @click="reset"
              >结束</el-button>
              <el-button
                v-if="pending"
                type="info"
                plain
                :disabled="Boolean(game_over)"
                @click="proceed"
              >继续</el-button>
              <el-button
                v-else
                type="info"
                plain
                :disabled="Boolean(game_over)"
                @click="pending = true"
              >暂停</el-button>

            </div>
          </el-card>
          <el-card
            class="box-card"
            v-else
          >
            <template #header>
              <div class="card-header">
                <span style="font-weight: bolder; font-size: 24px; color: #6ac8ff; user-select: none;">模式</span>
                <div>
                  <el-button
                    size="large"
                    link
                    class="button"
                    @click="startPlay"
                  >
                    <el-icon
                      :size="20"
                      color="#6ac8ff"
                    >
                      <VideoPlay />
                    </el-icon>
                  </el-button>
                  <el-button
                    size="large"
                    link
                    class="button"
                    @click="clearChessBoard"
                  >
                    <el-icon
                      :size="20"
                      color="#6ac8ff"
                    >
                      <Delete />
                    </el-icon>
                  </el-button>
                </div>
              </div>
            </template>
            <div class="button-group">
              <div class="mode-button">
                <el-button
                  style="width: 80%; margin-right: 20px;"
                  type="info"
                  size="large"
                  @click="newStart"
                >新的开始</el-button>
              </div>
              <div class="mode-button">
                <el-button
                  style="width: 80%; margin-right: 20px;"
                  type="info"
                  size="large"
                  @click="readEndgame"
                >经典残局</el-button>
              </div>
              <div class="mode-button">
                <el-button
                  style="width: 80%; margin-right: 20px;"
                  type="info"
                  size="large"
                  @click="readFile"
                >读取存档</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <canvas
            id="canvas"
            style="border: 1px solid;"
            width="500"
            height="500"
            :disabled="Boolean(game_over)"
            @dragover="allowDrop"
            @drop="dropPiece"
          ></canvas>
        </el-col>
        <el-col :span="1">
          <el-icon
            style="padding-top: 15px;"
            :size="40"
            color="#409EFC"
            v-if="turn"
          >
            <CaretRight />
          </el-icon>
          <el-icon
            style="padding-top: 328px; "
            :size="40"
            color="#409EFC"
            v-else
          >
            <CaretRight />
          </el-icon>
        </el-col>
        <el-col
          :span="7"
          class="player"
        >
          <div class="player-box">
            <div class="player-card">
              <el-avatar
                shape="square"
                :size=70
              >
                <p class="avatar">{{ this.player[1][0] }}</p>
              </el-avatar>
              <div class="name_card">
                <span class="name"> {{ this.player[1] }} </span>
                <p>
                  <el-button
                    size="small"
                    @click="editPlayer(1)"
                  >修改</el-button>
                  <el-button
                    size="small"
                    @click="changePlayer(1)"
                  >切换</el-button>
                </p>
              </div>
            </div>
            <div>
              <div class="tomb">
                <div
                  class="dead"
                  v-for="(piece, index) in dead.black.slice(0,8)"
                  :key="index"
                  @dragstart="dragPiece($event,'black',piece,index)"
                >
                  <el-popover
                    placement="top-start"
                    trigger="hover"
                    :width="150"
                    effect="dark"
                    :content="piece"
                  >
                    <template #reference>
                      <el-avatar
                        :size="32"
                        :src="'../../black_' + piece + '.png'"
                      />
                    </template>
                  </el-popover>
                </div>
              </div>
              <div class="tomb">
                <div
                  class="dead"
                  v-for="(piece, index) in dead.black.slice(8,16)"
                  :key="index"
                  @dragstart="dragPiece($event,'black',piece,index+8)"
                >
                  <el-popover
                    placement="top-start"
                    trigger="hover"
                    :width="150"
                    effect="dark"
                    :content="piece"
                  >
                    <template #reference>
                      <el-avatar
                        :size="32"
                        :src="'../../black_' + piece + '.png'"
                      />
                    </template>
                  </el-popover>
                </div>
              </div>
            </div>
          </div>
          <div
            class="player-box"
            style="position: relative;"
          >
            <div
              class="player-card"
              style="position: absolute; bottom: 0px;"
            >
              <el-avatar
                shape="square"
                :size=70
              >
                <p class="avatar">{{ this.player[0][0] }}</p>
              </el-avatar>
              <div class="name_card">
                <span class="name"> {{ this.player[0] }} </span>
                <p>
                  <el-button
                    size="small"
                    @click="editPlayer(0)"
                  >修改</el-button>
                  <el-button
                    size="small"
                    @click="changePlayer(0)"
                  >切换</el-button>
                </p>
              </div>
            </div>
            <div style="position: absolute; bottom: 94px;">
              <div class="tomb">
                <div
                  class="dead"
                  v-for="(piece, index) in dead.white.slice(0,8)"
                  :key="index"
                  @dragstart="dragPiece($event,'white',piece,index)"
                >
                  <el-popover
                    placement="top-start"
                    trigger="hover"
                    :width="150"
                    effect="dark"
                    :content="piece"
                  >
                    <template #reference>
                      <el-avatar
                        :size="32"
                        :src="'../../white_' + piece + '.png'"
                      />
                    </template>
                  </el-popover>

                </div>
              </div>
              <div class="tomb">
                <div
                  class="dead"
                  v-for="(piece, index) in dead.white.slice(8,16)"
                  :key="index"
                  @dragstart="dragPiece($event,'white',piece,index+8)"
                >
                  <el-popover
                    placement="top-start"
                    trigger="hover"
                    :width="150"
                    effect="dark"
                    :content="piece"
                  >
                    <template #reference>
                      <el-avatar
                        :size="32"
                        :src="'../../white_' + piece + '.png'"
                      />
                    </template>
                  </el-popover>
                </div>
              </div>
            </div>
          </div>

        </el-col>
      </el-row>

      <el-dialog
        v-model="changePlayerDialog"
        :title="'切换玩家' + (player_index + 1)"
        width="30%"
        @close="changeAgent(player_index)"
      >
        <el-select v-model="player[player_index]">
          <el-option
            v-for="agent in agents"
            :key="agent"
            :label="agent"
            :value="agent"
          />
        </el-select>
      </el-dialog>

      <el-dialog
        v-model="gameoverDialog"
        title="游戏结束"
        width="30%"
      >
        <h1>
          {{ '玩家' + game_over + '胜利' }}
        </h1>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="gameoverDialog = false">取消</el-button>
            <el-button
              type="primary"
              @click="reset"
            >重置</el-button>
          </span>
        </template>
      </el-dialog>

      <el-dialog
        v-model="saveDialog"
        title="保存"
        width="30%"
      >
        <el-input
          v-model="chessboard_name"
          placeholder="请输入棋局名称"
        ><template #append>
            <el-button @click="saveChessBoard">确定</el-button>
          </template>
          <template #prepend>棋局</template>
        </el-input>
      </el-dialog>

      <el-dialog
        v-model="gameListDialog"
        title="选择棋局"
      >
        <el-table
          :data="game_list"
          empty-text="暂无数据"
          stripe
          border
          highlight-current-row
          @current-change="chooseEndgame"
        >
          <el-table-column
            prop="id"
            label="编号"
            align="center"
            header-align="center"
            width="60"
          />
          <el-table-column
            prop="name"
            label="名称"
            align="center"
            header-align="center"
          />
          <el-table-column
            label="先手"
            align="center"
            header-align="center"
          >
            <template #default="scope">
              <div v-if="!scope.row.turn">
                白子
              </div>
              <div v-else>黑子</div>
            </template>
          </el-table-column>
          <el-table-column
            align="center"
            header-align="center"
            label="操作"
            v-if="endgame_type==1"
          >
            <template #default="scope">
              <el-popconfirm
                title="此操作不可撤销，是否继续？"
                confirm-button-text="确定"
                cancel-button-text="取消"
                @confirm="deleteEndgame(scope.row)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    <el-icon>
                      <Delete />
                    </el-icon>删除
                  </el-button>
                </template>
              </el-popconfirm>

            </template>
          </el-table-column>
        </el-table>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="gameListDialog = false">取消</el-button>
            <el-button
              type="primary"
              @click="startEndgame"
              :disabled="!endgame.id"
            >确定</el-button>
          </span>
        </template>
      </el-dialog>

      <el-dialog
        v-model="configDialog"
        :title="'修改玩家' + (player_index + 1) + '配置'"
        width="350px"
        @close="editAgent(player_index)"
      >
        <el-form
          :model="player_config[player_index]"
          label-width="80px"
          label-position="right"
        >
          <el-form-item
            v-for="(value,key) in string_item"
            :key="key"
            :label="key"
          >
            <el-select
              v-model="player_config[player_index][key]"
              style="width:200px"
            >
              <el-option
                v-for="v in value"
                :key="v"
                :label="v"
                :value="v"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            v-for="(value,key) in numeric_item"
            :key="key"
            :label="key"
          >
            <el-input-number
              v-model="player_config[player_index][key]"
              style="width:200px"
              :min="value[0]"
              :max="value[1]"
              controls-position="right"
              :step="1"
              step-strictly
              :label="key"
            />
          </el-form-item>
        </el-form>

      </el-dialog>

    </el-main>
    <Footer />
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'

import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

import Figure from '@/utils/chess'
import '@/utils/array'

export default {
  name: 'Main',
  components: {
    Header,
    Footer
  },
  data: function () {
    return {
      config: {
        margin: 0,
        size: 384,
        border_width: 2,
        white_block_color: [45, 77, 86],
        black_block_color: [0, 0, 0],
        thickness: 2,
        blood_color: [255, 0, 0],
        blood_width: 2
      },
      dead: {
        white: ['pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn',
          'rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'],
        black: ['pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn',
          'rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'],
      },
      turn: false,
      game_start: false,
      game_over: 0,
      logData: [],
      chessboard: {},
      figure: null,
      player: ['BeamSearch', 'Greedy'],
      player_config: [{}, {}],
      player_index: 0,
      agents: [],
      changePlayerDialog: false,
      gameoverDialog: false,
      saveDialog: false,
      gameListDialog: false,
      configDialog: false,
      actions: [],
      sources: [],
      targets: [],
      optional_sources: [],
      optional_targets: [],
      chessboard_name: '',
      game_list: [],
      endgame: {},
      is_new_game: true,
      endgame_turn: false,
      endgame_type: 0,
      pending: false,
      numeric_item: {},
      string_item: {},
    }
  },
  methods: {
    format: function (chessboard) {
      let data = []
      for (let i = 0; i < 8; i++) {
        for (let j = 0; j < 8; j++) {
          let piece = chessboard[`${i + 1}${j + 1}`]
          if (piece) {
            data.push([[piece[0], piece[1]], [[i + 1, j + 1, 1]]])
          }
        }
      }
      return data
    },
    proceed: async function () {
      this.pending = false
      if (this.game_start && !this.game_over) {
        await this.playChess()
      }
    },
    chooseEndgame: function (row) {
      if (row) {
        this.endgame = {
          id: row.id, turn: row.turn
        }
      }
    },
    readEndgame: async function () {
      this.endgame = {}
      try {
        let res = await axios.get("/api/endgame/0/")
        this.game_list = res.data
      } catch {
        ElMessage({
          message: '读取失败',
          type: 'error',
          offset: 100,
          duration: 3000
        })
      }

      this.endgame_type = 0
      this.gameListDialog = true
    },
    readFile: async function () {
      this.endgame = {}
      try {
        let res = await axios.get("/api/endgame/1/")
        this.game_list = res.data
      } catch {
        ElMessage({
          message: '读取失败',
          type: 'error',
          offset: 100,
          duration: 3000
        })
      }
      this.endgame_type = 1
      this.gameListDialog = true
    },
    saveChessBoard: async function () {
      await axios.get(`/api/save/${this.chessboard_name}/`)
      this.saveDialog = false
    },
    reset: async function () {
      this.gameoverDialog = false
      this.game_start = false
      this.game_over = 0
      this.pending = true
      this.is_new_game = true
      this.chessboard = {}
      this.figure.init()
      await axios.get("/api/end/")
      this.clearChessBoard()
    },
    startEndgame: async function () {
      this.gameListDialog = false
      this.is_new_game = false
      let res = await axios.get(`/api/load/${this.endgame.id}/`)
      this.chessboard = res.data.chessboard
      this.dead = res.data.dead
      this.turn = this.endgame.turn
      this.figure.draw(this.chessboard)
    },
    deleteEndgame: async function (row) {
      if (row && row.id) {
        try {
          await axios.delete(`/api/endgame/${row.id}/`)
          this.game_list = this.game_list.filter((g) => g.id != row.id)
        } catch {
          ElMessage({
            message: '删除失败',
            type: 'error',
            offset: 100,
            duration: 3000
          })
        }

      }
    },
    startPlay: async function () {
      this.pending = false
      this.game_start = true
      this.game_over = 0
      this.logData = []
      if (this.is_new_game) {
        this.turn = false
        if (this.dead.white.indexOf('king') >= 0 || this.dead.black.indexOf('king') >= 0) {
          ElMessage({
            message: '棋盘上缺少国王',
            type: 'error',
            offset: 100,
            duration: 3000
          })
          this.game_start = false
          return
        }
        let data = this.format(this.chessboard)
        await axios.post('/api/init_chessboard/', { data })
        this.endgame_turn = false
      } else {
        this.endgame_turn = this.turn
      }
      await this.playChess()
    },
    sleep: function (ms) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve()
        }, ms)
      })
    },
    undo: async function () {
      try {
        let res = await axios.get('/api/undo/')
        this.chessboard = res.data.chessboard
        this.dead = res.data.dead
        this.game_over = 0
        this.turn = !this.turn
        if (this.turn == this.endgame_turn) {
          this.logData.pop()
        } else {
          this.logData.slice(-1)[0].black = null
        }
        this.figure.draw(this.chessboard)
      } catch {
        ElMessage({
          message: '服务器内部错误，撤销失败',
          type: 'error',
          offset: 100,
          duration: 3000
        })
      }

      let agent = this.player[Number(this.turn)]
      if (agent == 'Human') {
        let res = await axios.get('/api/actions/')
        this.actions = res.data
        this.sources = []
        this.targets = []
        this.optional_sources = []
        this.optional_targets = []
        this.actions.forEach((a) => {
          if (a[0].length == 1) {
            this.optional_sources.push(a[0])
          }
        })
      }
    },
    playChess: async function (source, target) {
      while (!this.pending) {
        this.actions = []
        let agent = this.player[Number(this.turn)]
        this.sources = []
        this.targets = []
        this.optional_sources = []
        this.optional_targets = []
        if (agent != 'Human' || (source && target)) {
          let start = (new Date()).getTime()
          try {
            let res = await axios.post('/api/run/', { source: source, target: target })
            let end = (new Date()).getTime()
            source = null
            target = null
            this.chessboard = res.data.chessboard
            this.dead = res.data.dead
            this.game_over = res.data.game_over

            if (this.turn == this.endgame_turn) {
              this.logData.push({ white: res.data.record, black: null })
            } else {
              this.logData.slice(-1)[0].black = res.data.record
            }
            this.figure.draw(this.chessboard)
            this.turn = !this.turn

            if (this.game_over) {
              this.gameOver()
              break
            }

            if ((end - start) / 1000 < 1) {
              await this.sleep(500)
            }
          } catch {
            if (this.game_start && !this.pending) {
              ElMessage({
                message: '服务器内部错误，请退出重试',
                type: 'error',
                offset: 100,
                duration: 3000
              })
            }
            this.pending = true
            break
          }
        } else {
          let res = await axios.get('/api/actions/')
          this.actions = res.data
          this.actions.forEach((a) => {
            if (a[0].length == 1) {
              this.optional_sources.push(a[0])
            }
          })
          break
        }
      }
    },
    gameOver: function () {
      this.gameoverDialog = true
      this.actions = []
    },
    clearChessBoard: function () {
      this.chessboard = {}
      this.dead = {
        white: ['pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn',
          'rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'],
        black: ['pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn',
          'rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'],
      }
      this.figure.draw()
    },
    changePlayer: function (index) {
      this.player_index = index
      this.changePlayerDialog = true
      this.pending = true
    },
    editPlayer: function (index) {
      this.player_index = index
      let config = this.player_config[index]
      let items = Object.keys(config).filter((c) => c.indexOf('.') < 0)
      if (items.length == 0) {
        ElMessage({
          message: '无可配置项',
          type: 'warning',
          offset: 100,
          duration: 3000
        })
        return
      }
      this.string_item = {}
      this.numeric_item = {}
      for (let i of items) {
        if (typeof (config[i]) == 'string') {
          this.string_item[i] = config[`${i}.optional`]
        } else {
          this.numeric_item[i] = config[`${i}.range`]
        }
      }
      this.configDialog = true
      this.pending = true
    },
    changeAgent: async function (index) {
      let agent = await axios.post(`/api/init_player/${index + 1}/`, { model: this.player[index], config: null })
      this.player_config[index] = agent.data
      await this.proceed()
    },
    editAgent: async function (index) {
      let config = {}
      for (let c in this.player_config[index]) {
        if (c.indexOf('.') == -1) {
          config[c] = this.player_config[index][c]
        }
      }
      let agent = await axios.post(`/api/init_player/${index + 1}/`, { model: this.player[index], config: config })
      this.player_config[index] = agent.data
      await this.proceed()
    },
    newStart: function () {
      this.is_new_game = true
      this.chessboard = {
        '11': ['white', 'rook', 1],
        '21': ['white', 'knight', 1],
        '31': ['white', 'bishop', 1],
        '41': ['white', 'queen', 1],
        '51': ['white', 'king', 1],
        '61': ['white', 'bishop', 1],
        '71': ['white', 'knight', 1],
        '81': ['white', 'rook', 1],

        '12': ['white', 'pawn', 1],
        '22': ['white', 'pawn', 1],
        '32': ['white', 'pawn', 1],
        '42': ['white', 'pawn', 1],
        '52': ['white', 'pawn', 1],
        '62': ['white', 'pawn', 1],
        '72': ['white', 'pawn', 1],
        '82': ['white', 'pawn', 1],

        '18': ['black', 'rook', 1],
        '28': ['black', 'knight', 1],
        '38': ['black', 'bishop', 1],
        '48': ['black', 'queen', 1],
        '58': ['black', 'king', 1],
        '68': ['black', 'bishop', 1],
        '78': ['black', 'knight', 1],
        '88': ['black', 'rook', 1],

        '17': ['black', 'pawn', 1],
        '27': ['black', 'pawn', 1],
        '37': ['black', 'pawn', 1],
        '47': ['black', 'pawn', 1],
        '57': ['black', 'pawn', 1],
        '67': ['black', 'pawn', 1],
        '77': ['black', 'pawn', 1],
        '87': ['black', 'pawn', 1],
      }
      this.dead = {
        white: [],
        black: []
      }
      this.figure.draw(this.chessboard)
    },
    allowDrop: function (event) {
      if (!this.game_start && this.is_new_game) {
        event.preventDefault()
      }
    },
    dragPiece: function (event, color, name, index) {
      event.dataTransfer.setData('Text', `${index}-${color}-${name}`)
    },
    dropPiece: function (event) {
      event.preventDefault()
      let { offsetX, offsetY } = event
      let { margin, size } = this.config
      let block_size = Math.floor((size - 2 * margin) / 8)
      let col = Math.floor((offsetX - margin) / block_size) + 1
      let row = 9 - (Math.floor((offsetY - margin) / block_size) + 1)
      if ((col >= 1 && col <= 8) && (row >= 1 && row <= 8)) {
        let [index, color, name] = event.dataTransfer.getData('Text').split('-')
        if (color == 'white') {
          this.dead.white.splice(index, 1)
        } else {
          this.dead.black.splice(index, 1)
        }
        this.chessboard[`${col}${row}`] = [color, name, 1]
        this.figure.draw(this.chessboard)
      }
    },
  },
  mounted: async function () {
    this.figure = new Figure("canvas", this.config)

    let listener = (place, mult_src, mult_dst) => {
      place = Array.from(place)

      let yellow = [245, 245, 220]  // source
      let green = [0, 255, 0] // optional_source
      let blue = [54, 166, 255] // optional_target

      let is_legal_source = false
      let is_legal_target = false

      is_legal_source = this.optional_sources.contain([place])
      is_legal_target = this.optional_targets.contain([place])
      if (!is_legal_source && !is_legal_target) {
        for (let a of this.actions) {
          if (a[0].length == 1 && a[0][0].equals(place)) {
            is_legal_source = true
            this.sources = []
            break
          }
        }
      }

      if (this.sources.contain([place])) {
        return
      }
      if (this.targets.contain([place])) {
        return
      }
      if (is_legal_source && (this.sources.length == 0 || (mult_src && this.sources.length < 2))) {
        this.sources.push(place)
        this.optional_sources = []
        this.optional_targets = []
        for (let action of this.actions) {
          if (action[0].contain(this.sources)) {
            if (action[0].length == this.sources.length) {
              this.optional_targets = this.optional_targets.concat(action[1])
            } else if (action[0].length > this.sources.length) {
              this.optional_sources = this.optional_sources.concat(action[0].minus(this.sources))
            }
          }
        }
      } else if (is_legal_target) {
        this.targets.push(place)
        this.optional_targets = [place]
        for (let action of this.actions) {
          if (this.sources[0].equals(action[0][0]) && action[1].contain(this.targets)) {
            if (action[1].length > this.targets.length) {
              this.optional_targets = this.optional_targets.concat(action[1].minus(this.targets))
            }
          }
        }
        if (!mult_dst || this.targets.length == 2 || this.optional_targets.length == 1) {
          this.playChess(this.sources, this.targets)
        }
      } else {
        this.sources = []
        this.targets = []
        this.optional_sources = []
        this.optional_targets = []
        this.actions.forEach((a) => {
          if (a[0].length == 1) {
            this.optional_sources.push(a[0])
          }
        })
        this.figure.reload()
      }

      let blocks = []
      if (this.sources.length > 0) {
        this.optional_sources.forEach((p) => {
          blocks.push([p, green])
        })
      }
      this.optional_targets.forEach((p) => {
        blocks.push([p, blue])
      })
      this.sources.forEach((p) => {
        blocks.push([p, yellow])
      })
      this.figure.checked(blocks)
    }
    this.figure.add_listener(listener)

    this.figure.draw()
    this.figure.drag((color, name) => {
      this.dead[color].push(name)
    }, () => this.game_start || !this.is_new_game)

    let data = await axios.get('/api/agents/')
    this.agents = data.data

    let agent1 = await axios.post('/api/init_player/1/', { model: this.player[0], config: null })
    this.player_config[0] = agent1.data
    let agent2 = await axios.post('/api/init_player/2/', { model: this.player[1], config: null })
    this.player_config[1] = agent2.data
  }
}
</script>

<style scoped>
.el-main {
  padding: 40px;
  padding-top: 80px;
  background-color: black;
}
.player {
  display: block;
  justify-content: left;
  padding-left: 20px;
}
.name {
  color: white;
  size: 20px;
  vertical-align: top;
  font-size: 24px;
  display: flex;
  justify-content: left;
}
.avatar {
  font-size: 36px;
  font-weight: bolder;
}
.player-box {
  width: 100%;
  height: 198px;
  min-height: 198px;
  max-height: 198px;
}
.player-card {
  display: flex;
}
.tomb {
  display: flex;
}
.dead {
  padding: 0 2px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.box-card {
  background-color: #152934;
  height: 384px;
  border-width: 0;
  width: 300px;
  margin-right: 20px;
  float: right;
}
.operation {
  display: flex;
  justify-content: right;
  padding: 20px;
}
.log-table {
  background-color: #152934;
}
.button-group {
  display: block;
  padding-top: 20px;
}
.mode-button {
  padding: 15px;
  width: 100%;
  display: flex;
  justify-content: center;
}
.name_card {
  padding-left: 20px;
  text-align: left;
}
</style>
