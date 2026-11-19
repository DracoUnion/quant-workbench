"""Qt 主题（QSS）。唯一 PySide6 依赖层。

金融感深色主题：深蓝/墨绿背景，青紫强调色，保持专业、可阅读。
"""

DARK_QSS = """
QWidget {
    background: #0f172a;
    color: #e2e8f0;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
}
QMainWindow {
    background: #0f172a;
}
QSplitter::handle {
    background: #334155;
    width: 2px;
}
QSplitter::handle:horizontal {
    width: 2px;
}

/* 顶栏 */
#TopBar {
    background: #1e293b;
    border-bottom: 1px solid #334155;
    min-height: 56px;
    max-height: 56px;
}
#TitleLabel {
    color: #f8fafc;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
#SubtitleLabel {
    color: #94a3b8;
    font-size: 12px;
}

/* 侧边导航 */
#NavList {
    background: #0f172a;
    border: none;
    outline: none;
    font-size: 13px;
}
#NavList::item {
    padding: 10px 14px;
    border-bottom: 1px solid #1e293b;
    color: #cbd5e1;
}
#NavList::item:selected {
    background: #1e293b;
    color: #818cf8;
    border-left: 3px solid #818cf8;
}
#NavList::item:hover {
    background: #1e293b;
    color: #f8fafc;
}

/* 右侧页面容器 */
#PageContainer {
    background: #0f172a;
}

/* 分类标题 */
#CategoryHeader {
    background: transparent;
    border: none;
    font-size: 15px;
    font-weight: 700;
    color: #818cf8;
    padding: 12px 16px 4px 16px;
}

/* 提示词卡片 */
#PromptCard {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 8px;
}
#PromptCard:hover {
    border-color: #818cf8;
    background: #1e1b4b;
}
#PromptTitle {
    color: #f8fafc;
    font-size: 14px;
    font-weight: 700;
}
#PromptDesc {
    color: #94a3b8;
    font-size: 12px;
    margin-top: 4px;
}
#PromptMeta {
    color: #64748b;
    font-size: 11px;
    margin-top: 6px;
}

/* 搜索框 */
#SearchInput {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e2e8f0;
    font-size: 13px;
}
#SearchInput:focus {
    border-color: #818cf8;
}

/* 详情页正文 */
#DetailView {
    background: #0f172a;
    border: none;
}
#DetailTitle {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 800;
    padding: 16px 16px 8px 16px;
}
#DetailMeta {
    color: #94a3b8;
    font-size: 12px;
    padding: 0 16px 12px 16px;
}
#DetailBody {
    color: #e2e8f0;
    font-size: 13px;
    line-height: 1.7;
    padding: 0 16px 16px 16px;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    margin: 0 16px 16px 16px;
}
#DetailBody a {
    color: #818cf8;
}

/* 按钮 */
#PrimaryButton {
    background: #818cf8;
    color: #0f172a;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 700;
    font-size: 13px;
    min-width: 90px;
}
#PrimaryButton:hover {
    background: #a5b4fc;
}
#SecondaryButton {
    background: #334155;
    color: #e2e8f0;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    min-width: 90px;
}
#SecondaryButton:hover {
    background: #475569;
}

/* 收藏星标 */
#FavoriteStar {
    color: #fbbf24;
    font-size: 14px;
    border: none;
    background: transparent;
    padding: 2px;
}
#FavoriteStar:checked {
    color: #f59e0b;
}

/* 空状态 */
#EmptyState {
    color: #64748b;
    font-size: 14px;
    padding: 40px;
    background: transparent;
    border: none;
    qproperty-alignment: AlignCenter;
}
"""

LIGHT_QSS = """
QWidget {
    background: #f8fafc;
    color: #0f172a;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
}
QMainWindow {
    background: #f8fafc;
}
QSplitter::handle {
    background: #cbd5e1;
    width: 2px;
}
#TopBar {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    min-height: 56px;
    max-height: 56px;
}
#TitleLabel {
    color: #0f172a;
    font-size: 17px;
    font-weight: 700;
}
#SubtitleLabel {
    color: #64748b;
    font-size: 12px;
}
#NavList {
    background: #ffffff;
    border: none;
    outline: none;
    font-size: 13px;
}
#NavList::item {
    padding: 10px 14px;
    border-bottom: 1px solid #f1f5f9;
    color: #475569;
}
#NavList::item:selected {
    background: #eff6ff;
    color: #2563eb;
    border-left: 3px solid #2563eb;
}
#NavList::item:hover {
    background: #f1f5f9;
    color: #0f172a;
}
#PageContainer {
    background: #f8fafc;
}
#CategoryHeader {
    background: transparent;
    border: none;
    font-size: 15px;
    font-weight: 700;
    color: #2563eb;
    padding: 12px 16px 4px 16px;
}
#PromptCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 8px;
}
#PromptCard:hover {
    border-color: #2563eb;
    background: #f8fafc;
}
#PromptTitle {
    color: #0f172a;
    font-size: 14px;
    font-weight: 700;
}
#PromptDesc {
    color: #64748b;
    font-size: 12px;
    margin-top: 4px;
}
#PromptMeta {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 6px;
}
#SearchInput {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    color: #0f172a;
    font-size: 13px;
}
#SearchInput:focus {
    border-color: #2563eb;
}
#DetailView {
    background: #f8fafc;
    border: none;
}
#DetailTitle {
    color: #0f172a;
    font-size: 20px;
    font-weight: 800;
    padding: 16px 16px 8px 16px;
}
#DetailMeta {
    color: #64748b;
    font-size: 12px;
    padding: 0 16px 12px 16px;
}
#DetailBody {
    color: #0f172a;
    font-size: 13px;
    line-height: 1.7;
    padding: 0 16px 16px 16px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin: 0 16px 16px 16px;
}
#DetailBody a {
    color: #2563eb;
}
#PrimaryButton {
    background: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 700;
    font-size: 13px;
    min-width: 90px;
}
#PrimaryButton:hover {
    background: #3b82f6;
}
#SecondaryButton {
    background: #f1f5f9;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    min-width: 90px;
}
#SecondaryButton:hover {
    background: #e2e8f0;
}
#FavoriteStar {
    color: #fbbf24;
    font-size: 14px;
    border: none;
    background: transparent;
    padding: 2px;
}
#FavoriteStar:checked {
    color: #d97706;
}
#EmptyState {
    color: #94a3b8;
    font-size: 14px;
    padding: 40px;
    background: transparent;
    border: none;
    qproperty-alignment: AlignCenter;
}
"""


def load_qss(theme: str = "dark") -> str:
    return DARK_QSS if theme == "dark" else LIGHT_QSS
