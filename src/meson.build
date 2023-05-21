pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'upsmonitor')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
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
  'window.py',
  'ups_action_row.py',
  'host_action_row.py',
  'ups_preferences_page.py',
  'host_preferences_page.py',
  'monitor_preferences_window.py',
  'service_model.py',
  'data_model.py',
  'add_new_server_box.py',
]

install_data(upsmonitor_sources, install_dir: moduledir)
