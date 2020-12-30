from decimal import Decimal
from event import QuoteEvent, TradeEvent, TickType
from PyQt5 import QtCore, QtWidgets, QtGui

class MarketWindow(QtWidgets.QTableWidget):
    tick_signal = QtCore.pyqtSignal(object)

    def __init__(self, ui_events_engine=None, parent=None):
        super(MarketWindow, self).__init__(parent)
        self.ui_events_engine = ui_events_engine
        self.setFont(QtGui.QFont("Helvetica [Cronyx]", 10))
        self.headers = ['instrument','bsize','bid','ask','asize','spread','last_price','size']
        self.color_trade_map = {'buy': QtGui.QColor(0,128,0), 'sell': QtGui.QColor(139,0,0)}
        self.init_table()
        self.tick_signal.connect(self.update_table)
        self.cellClicked.connect(self.cell_clicked)
        self.awaited_buttons = []                      # tracks buttons waiting for server response to strategy start/stop

    @QtCore.pyqtSlot()
    def activate_clicked(self):
        button = self.sender()
        index = self.indexAt(button.pos())
        instrument_index = index.sibling(index.row(), 0)
        instrument = self.itemFromIndex(instrument_index).text()
        # get sym, exchange and current status
        # index = self.indexAt(button.pos())
        # if index.isValid():
        #     sym = self.item(index.row(), self.headers.index('sym'))
        #     exchange = self.item(index.row(), self.headers.index('exchange'))
        #     s = StrategyStatusEvent()
        #     s.deserialize(sym.text(), exchange.text(), button.text())
        #     self._ui_events_engine.put(s)

    def cell_clicked(self, row, column):
        if column == 0:
            item = self.item(row, column)
            name  = item.text()
            print(f'cell clicked {row} {column} instrument full_name={name}')

    def quantize_decimal(self, d):
        PLACES = Decimal(10) ** -10     # same as Decimal ('0.00000001')
        return str(Decimal(d).quantize(PLACES)).rstrip('0')

    def init_table(self):
        row = len(self.instrument_list)
        col = len(self.headers)
        self.setRowCount(row)
        self.setColumnCount(col)
        self.setHorizontalHeaderLabels(self.headers)
        self.horizontalHeader().setStyleSheet("::section{Background-color:rgb(102,102,255);border:2px solid rgb(204,179,255);border-radius:2px;border-style: inset;}")
        self.setEditTriggers(self.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        # set sizes
        self.setColumnWidth(self.headers.index('instrument'), 125)
        self.setColumnWidth(self.headers.index('bsize'), 85)
        self.setColumnWidth(self.headers.index('bid'), 77)
        self.setColumnWidth(self.headers.index('ask'), 77)
        self.setColumnWidth(self.headers.index('asize'), 85)
        self.setColumnWidth(self.headers.index('spread'), 68)
        self.setColumnWidth(self.headers.index('price'), 66)
        self.setColumnWidth(self.headers.index('size'), 80)
        for i in range(row):
            self.setItem(i, 0, QtWidgets.QTableWidgetItem(self.instrument_list[i])) # instrument full_name
            for j in range(1, col):
                self.setItem(i, j, QtWidgets.QTableWidgetItem(0.0))
                # activate button
                if j == self.headers.index('activate'):
                    activate_button = QtWidgets.QPushButton('Off')
                    self.setCellWidget(i, j, activate_button)
                    activate_button.clicked.connect(self.activate_clicked)

            exch = self.instrument_list[i].split("-")[0].lower()
            # set cell background colors
            # self.item(i, 0).setBackground(self.color_exch_map[exch])  # exch background
            self.item(i, 2).setBackground(QtGui.QColor(70,130,180))     # bid background
            self.item(i, 3).setBackground(QtGui.QColor(210,105,30))     # ask background
            self.item(i, 2).setForeground(QtGui.QColor(0,0,0))          # bid foreground
            self.item(i, 3).setForeground(QtGui.QColor(0,0,0))          # ask foreground


    def update_table(self, tickevent):
        try:
            row = self.instrument_list.index(tickevent.full_name)
            if tickevent.tick_type == TickType.TRADE:
                self.item(row, 6).setText(self.quantize_decimal(tickevent.price))
                self.item(row, 7).setText(self.quantize_decimal(tickevent.size))
                # color side background color on trade events
                c = self.color_trade_map[tickevent.side]
                self.item(row, 6).setBackground(c)
                self.item(row, 7).setBackground(c)
            elif tickevent.tick_type == TickType.QUOTE:
                self.item(row, 1).setText(self.quantize_decimal(tickevent.bid_size))
                self.item(row, 2).setText(self.quantize_decimal(tickevent.bid_price))
                self.item(row, 3).setText(self.quantize_decimal(tickevent.ask_price))
                self.item(row, 4).setText(self.quantize_decimal(tickevent.ask_size))
                # self.item(row, 5).setText(self.quantize_decimal(tickevent.spread))
        except ValueError as e:
            pass
            # print(f"VALUE ERROR!!!! Cannot find {tickevent.full_name} in {self.instrument_list}")


