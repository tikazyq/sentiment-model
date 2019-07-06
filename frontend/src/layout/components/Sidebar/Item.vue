<script>
export default {
  name: 'MenuItem',
  functional: true,
  props: {
    icon: {
      type: String,
      default: ''
    },
    className: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    }
  },
  render(h, context) {
    const { icon, title, className } = context.props
    const vnodes = []

    if (icon) {
      vnodes.push(<svg-icon icon-class={icon}/>)
    }

    if (className) {
      vnodes.push(<span class={className}/>)
    }

    if (title) {
      vnodes.push(<span slot='title'>{(title)}</span>)
    }
    return vnodes
  }
}
</script>
