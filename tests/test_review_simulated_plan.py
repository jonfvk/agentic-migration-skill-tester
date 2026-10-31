import unittest
from agentic_migration_skill_tester.migration_parser import MigrationInstructionParser
from agentic_migration_skill_tester.change_summarizer import ChangeSummarizer
from agentic_migration_skill_tester.in_memory_project import InMemoryProject

class TestReviewSimulatedMigrationPlan(unittest.TestCase):
    def setUp(self):
        # Simulate an initial project with two files
        self.initial_files = {
            'main.py': 'print("Hello")',
            'utils.py': 'def add(a, b): return a + b'
        }
        self.project = InMemoryProject(initial_files=self.initial_files)

    def test_review_plan_add_modify_delete(self):
        # Simulate migration instructions
        instruction_text = (
            'ADD new_module.py: def foo(): return 42\n'
            'MODIFY main.py: print("Hello, world!")\n'
            'DELETE utils.py\n'
            'UPDATE DEPENDENCY requests: 2.28.0\n'
        )
        steps = MigrationInstructionParser.parse_instructions(instruction_text)
        summarizer = ChangeSummarizer(steps)
        summary = summarizer.summarize()
        summary_dict = summary.to_dict()

        # User review: check the summary structure and content
        self.assertIn('added_files', summary_dict)
        self.assertIn('modified_files', summary_dict)
        self.assertIn('deleted_files', summary_dict)
        self.assertIn('updated_dependencies', summary_dict)
        self.assertIn('details', summary_dict)

        self.assertEqual(summary_dict['added_files'], ['new_module.py'])
        self.assertEqual(summary_dict['modified_files'], ['main.py'])
        self.assertEqual(summary_dict['deleted_files'], ['utils.py'])
        self.assertEqual(summary_dict['updated_dependencies'], {'requests': '2.28.0'})
        self.assertEqual(len(summary_dict['details']), 4)
        # Check that each step has a description for review
        for detail in summary_dict['details']:
            self.assertIn('description', detail)
            self.assertTrue(detail['description'])

    def test_review_plan_unknown_action(self):
        # Simulate an unknown action in the migration steps
        instruction_text = (
            'ADD foo.py: pass\n'
            'RENAME bar.py: baz.py\n'  # Not a supported action
        )
        with self.assertRaises(Exception):
            MigrationInstructionParser.parse_instructions(instruction_text)

    def test_review_plan_multiple_steps(self):
        instruction_text = (
            'ADD a.py: print(1)\n'
            'ADD b.py: print(2)\n'
            'MODIFY a.py: print(3)\n'
            'DELETE b.py\n'
        )
        steps = MigrationInstructionParser.parse_instructions(instruction_text)
        summarizer = ChangeSummarizer(steps)
        summary = summarizer.summarize()
        summary_dict = summary.to_dict()
        self.assertEqual(set(summary_dict['added_files']), {'a.py', 'b.py'})
        self.assertEqual(summary_dict['modified_files'], ['a.py'])
        self.assertEqual(summary_dict['deleted_files'], ['b.py'])
        self.assertEqual(summary_dict['updated_dependencies'], {})
        self.assertEqual(len(summary_dict['details']), 4)

    def test_review_plan_empty(self):
        # No migration steps
        steps = []
        summarizer = ChangeSummarizer(steps)
        summary = summarizer.summarize()
        summary_dict = summary.to_dict()
        self.assertEqual(summary_dict['added_files'], [])
        self.assertEqual(summary_dict['modified_files'], [])
        self.assertEqual(summary_dict['deleted_files'], [])
        self.assertEqual(summary_dict['updated_dependencies'], {})
        self.assertEqual(summary_dict['details'], [])

if __name__ == '__main__':
    unittest.main()
