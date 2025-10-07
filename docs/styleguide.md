# 🎨 UI Style Guide — Tech-Soft Pink Theme

## Color Palette
| Element | Color | Usage |
|----------|--------|--------|
| Primary | #F7C8E0 | Buttons / Highlights |
| Accent | #FF77C9 | Active states |
| Base Gray | #E4E4E7 | Background / Border |
| Glow Blue | #D7E3F4 | Subtle shadows |

## Button
```vue
<template>
  <button class="btn-tech"><slot/></button>
</template>

<style scoped>
.btn-tech {
  background: linear-gradient(135deg, #f7c8e0, #e4e4e7);
  border: 1px solid rgba(255,255,255,0.6);
  color: #222;
  font-weight: 500;
  padding: 10px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(255,119,201,0.25);
  transition: 0.2s ease;
}
.btn-tech:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(255,119,201,0.4);
}
.btn-tech:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
```
