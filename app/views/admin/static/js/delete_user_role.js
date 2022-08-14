const modalDeleteUserRole = document.getElementById('modalDeleteUserRole')
modalDeleteUserRole.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget
  const url = button.getAttribute('data-bs-url')
  const btn_delete = document.getElementById('btn-modal-delete')
  btn_delete.href = url
})