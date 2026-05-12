// Тема : Сплайны, интерполяция, аппроксимация.
// Задача : Реализовать интерактивную среду демонстрации параметрических кубических кривых(интерполяция, uniform B - spline, Катмулла - Рома).
// Дополнительно : рациональные кривые и веса.
// Теория : ПолиномыБернштейна, базисныефункцииB - сплайнов, интерполяция Лагранжа или Эрмита, влияние весовых коэффициентов.
// Задачи : 
// – Задача А : Только кривая Безье по 4 точкам.Отображение характеристической ломаной.
// – Задача Б : Возможность переключения между тремя типами : Безье(произвольное кол - во точек), B - Spline, Катмулл - Ром.Добавление / удаление точек.
// – Задача В : Реализация рациональных кривых(NURBS) с редактированием весов(ползунок для выбранной точки).Демонстрация влияния веса на форму кривой.

#pragma once
#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include <iostream>
#include <vector>
#include <cmath>
#include <functional>
#include <sstream>
#include <iomanip>

namespace task11 {

	class task11 {

	private:
		struct ControlPoint {
			sf::Vector2f position;
			float weight;
			bool selected;

			ControlPoint() : position(0.f, 0.f), weight(1.0f), selected(false) {}
			ControlPoint(float x, float y) : position(x, y), weight(1.0f), selected(false) {}
			ControlPoint(float x, float y, float w) : position(x, y), weight(w), selected(false) {}
			ControlPoint(sf::Vector2f pos) : position(pos), weight(1.0f), selected(false) {}
		};

		int binomial(int n, int k) {
			if (k == 0 || k == n) return 1;
			int result = 1;
			for (int i = 1; i <= k; ++i) {
				result = result * (n - i + 1) / i;
			}
			return result;
		}

		float bernstein(int i, int n, float t) {
			return binomial(n, i) * std::pow(t, i) * std::pow(1 - t, n - i);
		}

		sf::Vector2f bezierPoint(const std::vector<ControlPoint>& points, float t) {
			sf::Vector2f result(0.f, 0.f);
			int n = points.size() - 1;
			for (int i = 0; i <= n; ++i) {
				float b = bernstein(i, n, t);
				result.x += b * points[i].position.x;
				result.y += b * points[i].position.y;
			}
			return result;
		}

		std::vector<ControlPoint> extendPointsBSpline(const std::vector<ControlPoint>& points) {
			std::vector<ControlPoint> extended;
			extended.push_back(points.front());
			extended.push_back(points.front());
			for (const auto& p : points) {
				extended.push_back(p);
			}
			extended.push_back(points.back()); 
			extended.push_back(points.back());
			return extended;
		}

		sf::Vector2f bSplineSegment(sf::Vector2f p0, sf::Vector2f p1,
			sf::Vector2f p2, sf::Vector2f p3, float t) {
			float t2 = t * t;
			float t3 = t2 * t;

			float b0 = (-t3 + 3 * t2 - 3 * t + 1) / 6.0f;
			float b1 = (3 * t3 - 6 * t2 + 4) / 6.0f;
			float b2 = (-3 * t3 + 3 * t2 + 3 * t + 1) / 6.0f;
			float b3 = t3 / 6.0f;

			return sf::Vector2f(
				b0 * p0.x + b1 * p1.x + b2 * p2.x + b3 * p3.x,
				b0 * p0.y + b1 * p1.y + b2 * p2.y + b3 * p3.y
			);
		}

		sf::Vector2f bSplinePoint(const std::vector<ControlPoint>& points, float t) {
			if (points.size() < 2) return sf::Vector2f(0, 0);

			std::vector<ControlPoint> ext = extendPointsBSpline(points);
			int n = ext.size();
			int segments = n - 3;

			float segment = t * segments;
			int segIndex = std::min(static_cast<int>(segment), segments - 1);
			float localT = segment - segIndex;

			sf::Vector2f p0 = ext[segIndex].position;
			sf::Vector2f p1 = ext[segIndex + 1].position;
			sf::Vector2f p2 = ext[segIndex + 2].position;
			sf::Vector2f p3 = ext[segIndex + 3].position;

			return bSplineSegment(p0, p1, p2, p3, localT);
		}

		sf::Vector2f catmullRomSegment(sf::Vector2f p0, sf::Vector2f p1,
			sf::Vector2f p2, sf::Vector2f p3, float t) {
			float t2 = t * t;
			float t3 = t2 * t;

			float q0 = -t3 + 2.0f * t2 - t;
			float q1 = 3.0f * t3 - 5.0f * t2 + 2.0f;
			float q2 = -3.0f * t3 + 4.0f * t2 + t;
			float q3 = t3 - t2;

			return sf::Vector2f(
				0.5f * (p0.x * q0 + p1.x * q1 + p2.x * q2 + p3.x * q3),
				0.5f * (p0.y * q0 + p1.y * q1 + p2.y * q2 + p3.y * q3)
			);
		}

		std::vector<ControlPoint> extendPointsCatmull(const std::vector<ControlPoint>& points) {
			std::vector<ControlPoint> extended;
			extended.push_back(points.front());
			for (const auto& p : points) {
				extended.push_back(p);
			}
			extended.push_back(points.back());
			return extended;
		}

		sf::Vector2f catmullRomPoint(const std::vector<ControlPoint>& points, float t) {
			if (points.size() < 2) return sf::Vector2f(0, 0);

			std::vector<ControlPoint> ext = extendPointsCatmull(points);
			int n = ext.size();
			int segments = n - 3;

			float segment = t * segments;
			int i = std::min(static_cast<int>(segment), segments - 1);
			float localT = segment - i;

			sf::Vector2f p0 = ext[i].position;
			sf::Vector2f p1 = ext[i + 1].position;
			sf::Vector2f p2 = ext[i + 2].position;
			sf::Vector2f p3 = ext[i + 3].position;

			return catmullRomSegment(p0, p1, p2, p3, localT);
		}

		sf::Vector2f rationalBezierPoint(const std::vector<ControlPoint>& points, float t) {
			sf::Vector2f numerator(0.f, 0.f);
			float denominator = 0.f;
			int n = points.size() - 1;

			for (int i = 0; i <= n; ++i) {
				float b = bernstein(i, n, t) * points[i].weight;
				numerator.x += b * points[i].position.x;
				numerator.y += b * points[i].position.y;
				denominator += b;
			}

			if (denominator != 0.f) {
				numerator.x /= denominator;
				numerator.y /= denominator;
			}
			return numerator;
		}

		void drawCurve(sf::RenderWindow& window, const std::vector<ControlPoint>& points,
			std::function<sf::Vector2f(const std::vector<ControlPoint>&, float)> curveFunc,
			sf::Color color = sf::Color::Green) {
			if (points.size() < 2) return;

			sf::VertexArray curve(sf::PrimitiveType::LineStrip);
			int steps = 400;
			for (int i = 0; i <= steps; ++i) {
				float t = static_cast<float>(i) / steps;
				sf::Vector2f point = curveFunc(points, t);
				sf::Vertex vertex;
				vertex.position = point;
				vertex.color = color;
				curve.append(vertex);
			}
			window.draw(curve);
		}

		void drawControlPolygon(sf::RenderWindow& window, const std::vector<ControlPoint>& points) {
			if (points.size() < 2) return;

			sf::VertexArray lines(sf::PrimitiveType::LineStrip);
			for (const auto& p : points) {
				sf::Vertex vertex;
				vertex.position = p.position;
				vertex.color = sf::Color(100, 100, 100);
				lines.append(vertex);
			}
			window.draw(lines);
		}

		void drawControlPoints(sf::RenderWindow& window, const std::vector<ControlPoint>& points) {
			for (const auto& p : points) {
				sf::CircleShape circle(6.f);
				circle.setOrigin(sf::Vector2f(6.f, 6.f));
				circle.setPosition(p.position);
				circle.setFillColor(p.selected ? sf::Color::Yellow : sf::Color::Red);
				circle.setOutlineThickness(2.f);
				circle.setOutlineColor(sf::Color::White);
				window.draw(circle);
			}
		}

		int getPointAtPosition(const std::vector<ControlPoint>& points, sf::Vector2f pos) {
			for (size_t i = 0; i < points.size(); ++i) {
				float dx = points[i].position.x - pos.x;
				float dy = points[i].position.y - pos.y;
				if (std::sqrt(dx * dx + dy * dy) < 10.f) {
					return static_cast<int>(i);
				}
			}
			return -1;
		}

		class Slider {
		public:
			sf::RectangleShape background;
			sf::RectangleShape handle;
			float minValue, maxValue, currentValue;
			bool isDragging;

			Slider(sf::Vector2f position, float width, float min, float max, float initial)
				: minValue(min), maxValue(max), currentValue(initial), isDragging(false) {

				background.setSize(sf::Vector2f(width, 10.f));
				background.setPosition(position);
				background.setFillColor(sf::Color(80, 80, 80));
				background.setOutlineColor(sf::Color::White);
				background.setOutlineThickness(1.f);

				handle.setSize(sf::Vector2f(15.f, 20.f));
				handle.setOrigin(sf::Vector2f(7.5f, 10.f));
				handle.setFillColor(sf::Color::Yellow);
				handle.setOutlineColor(sf::Color::White);
				handle.setOutlineThickness(2.f);

				updateHandlePosition();
			}

			void updateHandlePosition() {
				float t = (currentValue - minValue) / (maxValue - minValue);
				float x = background.getPosition().x + t * background.getSize().x;
				handle.setPosition(sf::Vector2f(x, background.getPosition().y + 5.f));
			}

			bool handleMousePressed(sf::Vector2f mousePos) {
				if (handle.getGlobalBounds().contains(mousePos)) {
					isDragging = true;
					return true;
				}
				return false;
			}

			void handleMouseReleased() {
				isDragging = false;
			}

			void handleMouseMoved(sf::Vector2f mousePos) {
				if (isDragging) {
					float x = mousePos.x;
					float bgLeft = background.getPosition().x;
					float bgRight = bgLeft + background.getSize().x;

					x = std::max(bgLeft, std::min(bgRight, x));
					float t = (x - bgLeft) / background.getSize().x;
					currentValue = minValue + t * (maxValue - minValue);
					updateHandlePosition();
				}
			}

			void draw(sf::RenderWindow& window, const std::string& text) {
				window.draw(background);
				window.draw(handle);
			}

			float getValue() const { return currentValue; }
			void setValue(float value) {
				currentValue = std::max(minValue, std::min(maxValue, value));
				updateHandlePosition();
			}
		};

		void taskA() {
			sf::RenderWindow window(sf::VideoMode({ 800, 800 }), "Task A - Bezier curve");
			window.setFramerateLimit(60);

			std::vector<ControlPoint> points;
			points.push_back(ControlPoint(200.f, 600.f));
			points.push_back(ControlPoint(200.f, 200.f));
			points.push_back(ControlPoint(600.f, 200.f));
			points.push_back(ControlPoint(600.f, 600.f));

			int draggedPoint = -1;

			while (window.isOpen())
			{
				while (const std::optional event = window.pollEvent())
				{
					if (event->is<sf::Event::Closed>())
						window.close();

					if (const auto* mousePressed = event->getIf<sf::Event::MouseButtonPressed>()) {
						if (mousePressed->button == sf::Mouse::Button::Left) {
							sf::Vector2f mousePos(static_cast<float>(mousePressed->position.x),
								static_cast<float>(mousePressed->position.y));
							draggedPoint = getPointAtPosition(points, mousePos);
						}
					}

					if (event->is<sf::Event::MouseButtonReleased>()) {
						draggedPoint = -1;
					}

					if (const auto* mouseMoved = event->getIf<sf::Event::MouseMoved>()) {
						if (draggedPoint != -1) {
							points[draggedPoint].position = sf::Vector2f(
								static_cast<float>(mouseMoved->position.x),
								static_cast<float>(mouseMoved->position.y)
							);
						}
					}
				}

				window.clear(sf::Color(30, 30, 40));

				drawControlPolygon(window, points);

				auto bezierFunc = [this](const std::vector<ControlPoint>& p, float t) {
					return bezierPoint(p, t);
					};
				drawCurve(window, points, bezierFunc);

				drawControlPoints(window, points);

				window.display();
			}
		}

		void taskB() {
			sf::RenderWindow window(sf::VideoMode({ 800, 800 }), "Task B - Bezier, B-Spline, Catmull-Rom");
			window.setFramerateLimit(60);

			std::vector<ControlPoint> points;
			points.push_back(ControlPoint(100.f, 400.f));
			points.push_back(ControlPoint(200.f, 200.f));
			points.push_back(ControlPoint(400.f, 300.f));
			points.push_back(ControlPoint(600.f, 200.f));
			points.push_back(ControlPoint(700.f, 500.f));

			int draggedPoint = -1;
			int selectedPoint = -1;
			int curveType = 0;
			const char* curveNames[] = { "Безье", "Б-Сплайн", "Катмул-Ром" };

			std::cout << "\n1 - Безье, 2 - Б-Сплайн, 3 - Катмул-Ром" << std::endl;
			std::cout << "ПКМ - Добавить точку, Delete - Удалить выбранную точку" << std::endl;

			while (window.isOpen())
			{
				while (const std::optional event = window.pollEvent())
				{
					if (event->is<sf::Event::Closed>())
						window.close();

					if (const auto* keyPressed = event->getIf<sf::Event::KeyPressed>()) {
						if (keyPressed->code == sf::Keyboard::Key::Num1) {
							curveType = 0;
							std::cout << "Переключение: " << curveNames[curveType] << std::endl;
						}
						else if (keyPressed->code == sf::Keyboard::Key::Num2) {
							curveType = 1;
							std::cout << "Переключение: " << curveNames[curveType] << std::endl;
						}
						else if (keyPressed->code == sf::Keyboard::Key::Num3) {
							curveType = 2;
							std::cout << "Переключение: " << curveNames[curveType] << std::endl;
						}
						else if (keyPressed->code == sf::Keyboard::Key::Delete && selectedPoint != -1) {
							points.erase(points.begin() + selectedPoint);
							selectedPoint = -1;
							draggedPoint = -1;
						}
					}

					if (const auto* mousePressed = event->getIf<sf::Event::MouseButtonPressed>()) {
						sf::Vector2f mousePos(static_cast<float>(mousePressed->position.x),
							static_cast<float>(mousePressed->position.y));

						if (mousePressed->button == sf::Mouse::Button::Left) {
							int clicked = getPointAtPosition(points, mousePos);
							if (clicked != -1) {
								draggedPoint = clicked;
								selectedPoint = clicked;
								for (auto& p : points) p.selected = false;
								points[selectedPoint].selected = true;
							}
						}
						else if (mousePressed->button == sf::Mouse::Button::Right) {
							points.push_back(ControlPoint(mousePos));
						}
					}

					if (event->is<sf::Event::MouseButtonReleased>()) {
						draggedPoint = -1;
					}

					if (const auto* mouseMoved = event->getIf<sf::Event::MouseMoved>()) {
						if (draggedPoint != -1) {
							points[draggedPoint].position = sf::Vector2f(
								static_cast<float>(mouseMoved->position.x),
								static_cast<float>(mouseMoved->position.y)
							);
						}
					}
				}

				window.clear(sf::Color(30, 30, 40));

				drawControlPolygon(window, points);

				if (curveType == 0) {
					auto bezierFunc = [this](const std::vector<ControlPoint>& p, float t) {
						return bezierPoint(p, t);
						};
					drawCurve(window, points, bezierFunc, sf::Color::Green);
				}
				else if (curveType == 1 && points.size() >= 2) {
					auto bSplineFunc = [this](const std::vector<ControlPoint>& p, float t) {
						return bSplinePoint(p, t);
						};
					drawCurve(window, points, bSplineFunc, sf::Color::Cyan);
				}
				else if (curveType == 2 && points.size() >= 2) {
					auto catmullFunc = [this](const std::vector<ControlPoint>& p, float t) {
						return catmullRomPoint(p, t);
						};
					drawCurve(window, points, catmullFunc, sf::Color::Magenta);
				}

				drawControlPoints(window, points);

				window.display();
			}
		}

		void taskC() {
			sf::RenderWindow window(sf::VideoMode({ 800, 850 }), "Task C - Rational curves");
			window.setFramerateLimit(60);

			std::vector<ControlPoint> points;
			points.push_back(ControlPoint(200.f, 600.f, 1.0f));
			points.push_back(ControlPoint(200.f, 200.f, 1.0f));
			points.push_back(ControlPoint(600.f, 200.f, 1.0f));
			points.push_back(ControlPoint(600.f, 600.f, 1.0f));

			int draggedPoint = -1;
			int selectedPoint = -1;

			Slider weightSlider(sf::Vector2f(50.f, 780.f), 700.f, 0.1f, 5.0f, 1.0f);

			while (window.isOpen())
			{
				while (const std::optional event = window.pollEvent())
				{
					if (event->is<sf::Event::Closed>())
						window.close();

					if (const auto* mousePressed = event->getIf<sf::Event::MouseButtonPressed>()) {
						sf::Vector2f mousePos(static_cast<float>(mousePressed->position.x),
							static_cast<float>(mousePressed->position.y));

						if (mousePressed->button == sf::Mouse::Button::Left) {
							if (weightSlider.handleMousePressed(mousePos)) {
							}
							else {
								int clicked = getPointAtPosition(points, mousePos);
								if (clicked != -1) {
									draggedPoint = clicked;
									for (auto& p : points) p.selected = false;
									points[clicked].selected = true;
									selectedPoint = clicked;
									weightSlider.setValue(points[selectedPoint].weight);

									std::cout << "Вес выбранной точки: " << std::fixed << std::setprecision(2)
										<< points[selectedPoint].weight << std::endl;
								}
							}
						}
					}

					if (event->is<sf::Event::MouseButtonReleased>()) {
						draggedPoint = -1;
						weightSlider.handleMouseReleased();
					}

					if (const auto* mouseMoved = event->getIf<sf::Event::MouseMoved>()) {
						sf::Vector2f mousePos(static_cast<float>(mouseMoved->position.x),
							static_cast<float>(mouseMoved->position.y));

						if (draggedPoint != -1 && draggedPoint < static_cast<int>(points.size())) {
							points[draggedPoint].position = mousePos;
						}

						weightSlider.handleMouseMoved(mousePos);
						if (selectedPoint != -1 && weightSlider.isDragging) {
							points[selectedPoint].weight = weightSlider.getValue();
						}
					}
				}

				window.clear(sf::Color(30, 30, 40));

				auto bezierFunc = [this](const std::vector<ControlPoint>& p, float t) {
					return bezierPoint(p, t);
					};
				drawCurve(window, points, bezierFunc, sf::Color(100, 100, 100));

				auto rationalFunc = [this](const std::vector<ControlPoint>& p, float t) {
					return rationalBezierPoint(p, t);
					};
				drawCurve(window, points, rationalFunc, sf::Color::Green);

				drawControlPolygon(window, points);
				drawControlPoints(window, points);

				std::string sliderLabel = selectedPoint != -1 ?
					"Weight of Point " + std::to_string(selectedPoint) : "Select a point";
				weightSlider.draw(window, sliderLabel);

				window.display();
			}
		}

	public:

		void processTask() {
			std::cout << "╔══════════════════════════════════════════════╗" << std::endl;
			std::cout << "║     СПЛАЙНЫ, ИНТЕРПОЛЯЦИЯ, АППРОКСИМАЦИЯ     ║" << std::endl;
			std::cout << "╠══════════════════════════════════════════════╣" << std::endl;
			std::cout << "║  1 - Кривая Безье                            ║" << std::endl;
			std::cout << "║  2 - Безье, Б-Сплайн, Катмул-Ром             ║" << std::endl;
			std::cout << "║  3 - Рациональные кривые                     ║" << std::endl;
			std::cout << "║  4 - Выход                                   ║" << std::endl;
			std::cout << "╚══════════════════════════════════════════════╝" << std::endl;
			std::string answer;
			bool stop = false;

			while (!stop) {
				std::cout << "\nВведите ответ: ";
				std::cin >> answer;
				if (answer == "1") {
					taskA();
				}
				else if (answer == "2") {
					taskB();
				}
				else if (answer == "3") {
					taskC();
				}
				else if (answer == "4") {
					stop = true;
					std::cout << "*** ЗАВЕРШЕНИЕ::ПРОГРАММА УСПЕШНО ЗАКОНЧИЛА РАБОТУ ***\n";
				}
				else {
					std::cout << " *** ОШИБКА::НЕВЕРНЫЙ ВАРИАНТ ОТВЕТА *** \n";
				}
			}
		}
	};
}