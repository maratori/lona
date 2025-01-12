/* MIT License

Copyright (c) 2020 Florian Scherf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/

import { LonaContext } from './context.js';


export class Lona {
    static settings = {};
    static protocol = {};
    static widget_classes = {};
    static LonaContext = LonaContext;

    static set_protocol(protocol) {
        for(const [key, value] of Object.entries(protocol)) {
            Lona.protocol[key] = value;
        };
    };

    static set_settings(settings) {
        for(const [key, value] of Object.entries(settings)) {
            Lona.settings[key] = value;
        };
    };

    static register_widget_class(widget_name, javascript_class) {
        Lona.widget_classes[widget_name] = javascript_class;
    };
};

window['Lona'] = Lona;
