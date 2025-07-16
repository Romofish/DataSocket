# ALS READER LOGIC
1. Display
    1.1 Order, fieldOID, PreText,
    1.2

    在log布局前出现了一些问题我需要反馈：

1.field.IsRequired灯等的意思是什么，页面更新后也没有显示出，我的逻辑是指这个field对应的isrequired column，位于上传的ALS文件的fields sheet

2.Datadictionary不是简单的姓名匹配，而是到对应的sheet，找到这个dictionary，再提取出它的user string，另外，如果specify栏是YES的话，意味着选中对应选项后，页面要出现一个空的文本框。

3.Restriction相关的两列，代表着不同的role看到的field不一样，可以entry的field也不一样，在页面右上角需要添加一个切换Role的选项，通过切换有不同显示，entryrestrction的role无法输入值，这个可以通过鼠标移动显示成禁止标注来表明

4.没有显示field的pretext，这是页面给CRC看的时候显示的东西，最好和fieldOID一起展示

5.页面还需要一个选项，切换显示fieldOID还是SAS label，或者是两者同时显示



我们还要花大量时间来处理这个预览逻辑，让我们一步步细化好嘛，包括剩余未做的Log和AI模块。