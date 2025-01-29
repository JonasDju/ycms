# Copyright [2019] [Integreat Project]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Constants are used whenever we store values in the database which are chosen from a very limited set.
Defining constants here adds an abstract layer on top of the actual values that are stored in the database.
This improves readability of the code, enables auto-completion of values and minimizes the risk of mistakes.
The actual values which are stored in the database are completely irrelevant, because neither the developer,
nor the end users gets to see them.
The developer only sees the defined constant, and the end user only sees the (translated) string representation
defined in a mapping which is called ``CHOICES`` for every submodule.
"""
