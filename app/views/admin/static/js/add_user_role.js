const modalAddUserRole = document.getElementById('modalAddUserRole')
modalAddUserRole.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget
  const url = button.getAttribute('data-bs-url')
  const btn_delete = document.getElementById('btn-modal-add')
  btn_delete.href = url
})