import contextlib
from kivy.lang import Builder
from kivy.logger import previous_stderr
from kivymd.app import MDApp
from prisma import Prisma
from prisma.models import Customer


class App(MDApp):
    def build(self) -> Builder:
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'BlueGray'

        # we need to un-monkeypatch stderr as client.connect()
        # opens a subprocess which will cause an error if the
        # kivy-patched stderr is used
        with contextlib.redirect_stderr(previous_stderr):
            # auto_register the client instance so that we can query
            # from model classes
            client = Prisma(auto_register=True)
            client.connect()

        return Builder.load_file('app.kv')

    def submit(self) -> None:
        Customer.prisma().create(
            data={
                'name': self.root.ids.word_input.text,
            },
        )

        # Add a little message
        self.root.ids.word_label.text = f'{self.root.ids.word_input.text} Added'

        # Clear the input box
        self.root.ids.word_input.text = ''

    def show_records(self) -> None:
        word = ''
        for customer in Customer.prisma().find_many():
            word = f'{word}\n{customer.name}'
            self.root.ids.word_label.text = f'{word}'


if __name__ == '__main__':
    App().run()
