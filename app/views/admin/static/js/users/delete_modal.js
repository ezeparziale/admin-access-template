const modalDeleteUser = document.getElementById('modalDeleteUser')
modalDeleteUser.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget
  const url = button.getAttribute('data-bs-url')
  const btn_delete = document.getElementById('btn-modal-delete')
  btn_delete.href = url

  const data_name = document.getElementById('data_name')
  data_name.innerHTML = button.getAttribute('data-bs-name')
});