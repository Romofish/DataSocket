ALS Form Previewer - Display Logic Documentation
ALS表单预览器 - 显示逻辑文档
English Version
1. Overview
This document explains the display logic for the ALS (Architect Loader Sheet) Form Previewer application. The application is built using Vue.js 3 (<script setup>) and Pinia for state management. Its primary purpose is to parse an .xlsx ALS file, and provide an interactive preview of the forms contained within, allowing for dynamic changes based on user role and display preferences.

2. Core Components
The application's display logic is primarily handled by three key files:

stores/alsStore.js: The Pinia store that acts as the central brain. It holds the parsed data and contains getters to prepare and compute data for the view.

views/AlsReaderView.vue: The main parent component. It manages the overall layout, UI controls (like role and mode selectors), and renders the list of fields by iterating over data from the store.

components/FormField.vue: A reusable child component responsible for rendering a single field. It contains all the complex conditional logic for displaying different field types, labels, and controls.

3. Data Flow
Parsing: The user uploads an .xlsx file. alsStore.js uses the XLSX library to parse the Forms, Fields, DataDictionaries, and DataDictionaryEntries sheets into JSON arrays.

State Update: The parsed data is stored in the Pinia state, and isParsed is set to true.

User Selection: The user selects a Form from the sidebar in AlsReaderView.vue.

Data Retrieval: AlsReaderView.vue's fieldsForPreview computed property calls the getFieldsForPreview getter from the store, passing the selected Form OID and the currently selected Role.

Data Preparation (getFieldsForPreview getter): This crucial getter processes the raw field data:

It filters all fields that belong to the selected FormOID.

It calculates field visibility (isVisible) and input restrictions (isEntryRestricted) based on the ViewRestrictions and EntryRestrictions columns for the selected role.

It generates a displayPrefix string (e.g., *, #, ^, $) for fields that are required or have query flags (IsRequired, QueryFutureDate, etc.).

It finds all associated dictionary entries for a field by matching DataDictionaryName in the Fields and DataDictionaryEntries sheets. These are attached as a dictionaryEntries array.

Rendering: AlsReaderView.vue receives the prepared array of fields. It then loops through this array and renders a <FormField> component for each field, passing down the field data and UI preferences (props).

4. Detailed Display Logic in FormField.vue
The FormField.vue component receives field, labelMode, and previewMode as props and applies the following logic:

4.1. Layout & Content Order
The component renders information in a fixed order:

Label Container: The top section containing the main field text.

Field Header: The section below the label containing the Field OID.

Control Wrapper: The final section containing the input control (e.g., textbox, dropdown).

4.2. Conditional Label Display
The content of the Label Container is determined by the labelMode prop:

Name (labelMode: 'DraftFieldName'): Displays only the field.DraftFieldName.

SAS Label (labelMode: 'SASLabel'): Displays only the field.SASLabel.

Both (labelMode: 'Both'): Displays field.DraftFieldName followed by [field.SASLabel].

Pre-Text: If field.PreText exists, it is always displayed below the main label, inside the Label Container.

4.3. Control Type Rendering
The component uses field.ControlType to render the appropriate HTML input element:

If ControlType is Long Text, it renders a <textarea>.

If ControlType is Text, it renders an <input type="text">.

For other types, it renders a fallback text input.

The placeholder for these inputs is populated with the field.DataFormat string from the ALS file.

4.4. Dictionary-Based Fields (Dropdowns/Radio Groups)
If a field has associated dictionaryEntries (i.e., a list of choices), its rendering is controlled by the previewMode prop:

Dropdown Mode (previewMode: 'dropdown'):

It renders a custom-built, clickable <button> that acts as a dropdown trigger.

The button's text shows the selected option's UserDataString or "Dropdown List" if nothing is selected.

Clicking the button toggles the visibility of a panel containing all the options, animated with a transition.

Flat Mode (previewMode: 'flat'):

It renders all options directly on the page as a vertical list of radio buttons (<input type="radio">).

Each option displays its UserDataString (or CodedData as a fallback).

The state of the selected option is managed internally and kept in sync across both modes.

4.5. "Specify" Field Handling
If a user selects a dictionary option where the Specify property is true, a text input box appears below the control, prompting the user for more details. This works seamlessly in both Dropdown and Flat modes as it depends only on the currently selected entry.

中文版本
1. 概览
本文件旨在说明 ALS (Architect Loader Sheet) 表单预览器应用的显示逻辑。该应用基于 Vue.js 3 (<script setup>) 和 Pinia (状态管理) 构建。其主要功能是解析 .xlsx 格式的 ALS 文件，并提供一个交互式的表单预览，允许用户根据角色和显示偏好动态地改变视图。

2. 核心组件
应用的显示逻辑主要由三个关键文件处理：

stores/alsStore.js: Pinia store，作为应用的数据中枢。它负责存储解析后的数据，并包含 getter 方法，用于为视图准备和计算数据。

views/AlsReaderView.vue: 主父组件。它管理整体布局和UI控件（如角色和模式选择器），并通过遍历 store 中的数据来渲染字段列表。

components/FormField.vue: 一个可复用的子组件，负责渲染单个字段。它包含了所有复杂的条件逻辑，用于显示不同的字段类型、标签和控件。

3. 数据流
解析: 用户上传一个 .xlsx 文件。alsStore.js 使用 XLSX 库将 Forms, Fields, DataDictionaries, DataDictionaryEntries 这几个工作表解析成 JSON 数组。

状态更新: 解析后的数据存储在 Pinia 的 state 中，同时 isParsed 状态位被设为 true。

用户选择: 用户在 AlsReaderView.vue 的侧边栏中选择一个表单 (Form)。

数据获取: AlsReaderView.vue 中的计算属性 fieldsForPreview 调用 store 中的 getFieldsForPreview getter，并传入当前选择的 Form OID 和角色。

数据准备 (getFieldsForPreview getter): 这个至关重要的 getter 方法负责处理原始字段数据：

它筛选出所有属于所选 FormOID 的字段。

它根据 ViewRestrictions 和 EntryRestrictions 列以及当前选择的角色，计算字段的可见性 (isVisible) 和输入限制 (isEntryRestricted)。

它为必填或有稽查查询标记的字段（如 IsRequired, QueryFutureDate 等）生成一个 displayPrefix 字符串（例如 *, #, ^, $）。

它通过匹配 Fields 和 DataDictionaryEntries 工作表中的 DataDictionaryName，为字段找到所有关联的数据字典条目。这些条目作为一个 dictionaryEntries 数组附加到字段对象上。

渲染: AlsReaderView.vue 接收准备好的字段数组。然后它遍历此数组，并为每个字段渲染一个 <FormField> 组件，同时将字段数据和UI偏好作为 props 传入。

4. FormField.vue 中的详细显示逻辑
FormField.vue 组件接收 field, labelMode, previewMode 作为 props，并应用以下逻辑：

4.1. 布局与内容顺序
组件以固定的顺序渲染信息：

标签容器 (Label Container): 位于最顶部的区域，包含字段的主要文本。

字段头部 (Field Header): 位于标签下方的区域，包含字段的 OID。

控件包装器 (Control Wrapper): 最后的区域，包含输入控件（如文本框、下拉菜单等）。

4.2. 条件化标签显示
标签容器 的内容由 labelMode prop 决定：

Name (labelMode: 'DraftFieldName'): 仅显示 field.DraftFieldName。

SAS Label (labelMode: 'SASLabel'): 仅显示 field.SASLabel。

Both (labelMode: 'Both'): 显示 field.DraftFieldName 后跟 [field.SASLabel]。

Pre-Text: 如果 field.PreText 存在，它将总是在主标签下方、标签容器内部显示。

4.3. 控件类型渲染
组件使用 field.ControlType 来渲染对应的 HTML 输入元素：

如果 ControlType 是 Long Text，则渲染一个 <textarea>。

如果 ControlType 是 Text，则渲染一个 <input type="text">。

对于其他类型，会渲染一个备用的文本输入框。

这些输入框的 placeholder (占位符) 会被填充为 ALS 文件中的 field.DataFormat 字符串。

4.4. 字典类字段 (下拉/单选)
如果一个字段有关联的 dictionaryEntries (即一个选项列表)，它的渲染方式由 previewMode prop 控制：

Dropdown 模式 (previewMode: 'dropdown'):

渲染一个自定义的、可点击的 <button> 作为下拉菜单的触发器。

按钮的文本显示当前选中项的 UserDataString，如果未选择任何项，则显示 "Dropdown List"。

点击按钮会切换一个包含所有选项的面板的可见性，并伴有动画过渡效果。

Flat 模式 (previewMode: 'flat'):

将所有选项作为垂直的单选按钮列表 (<input type="radio">) 直接在页面上渲染出来。

每个选项显示其 UserDataString (如果不存在则显示 CodedData)。

选中项的状态在组件内部进行管理，并能在两种模式间保持同步。

4.5. "Specify" 字段处理
如果用户选择了一个 Specify 属性为 true 的字典选项，一个文本输入框会出现在控件下方，提示用户输入更详细的信息。此功能在 Dropdown 和 Flat 两种模式下都能无缝工作，因为它仅依赖于当前选中的条目。