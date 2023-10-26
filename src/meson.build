pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'upsmonitor')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'upsmonitor.in',
  output: 'upsmonitor',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

upsmonitor_sources = [
  '__init__.py',
  'main.py',
  'gui/window.py',
  'gui/ups_pages.py',
  'gui/host_pages.py',
  'gui/add_new_server_box.py',
  'gui/monitor_preferences_window.py',
  'service/ups_monitor_daemon.py',
  'service/data_service.py',
  'model/data_model.py',
  'model/exception_model.py',
]

install_data(upsmonitor_sources, install_dir: moduledir)
