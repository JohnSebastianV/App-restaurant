document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const url = btn.dataset.url;
      Swal.fire({
        title: '¿Estás seguro?',
        text: "¡No podrás revertir esto!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          fetch(url, { method: 'POST' })
            .then(response => {
              if(response.ok) {
                Swal.fire('Eliminado!', 'Se eliminó correctamente.', 'success')
                  .then(() => window.location.href = '/dashboard');
              }
            });
        }
      });
    });
  });
});

